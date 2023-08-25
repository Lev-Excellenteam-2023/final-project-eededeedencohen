from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, BLOB, text
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSON  # Import the JSON type
import uuid
from datetime import datetime
import os


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False)

    # Relationships
    uploads = relationship("Upload", back_populates="user")


class Upload(Base):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(String, default=str(uuid.uuid4()), nullable=False)
    filename = Column(String, nullable=False)
    upload_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    finish_time = Column(DateTime, nullable=True)
    status = Column(String, nullable=False)  # Updated the nullable parameter
    user_id = Column(Integer, ForeignKey("users.id"))
    explanation = Column(JSON, default="None")

    # Relationships
    user = relationship("User", back_populates="uploads")
    file = relationship("Files", uselist=False, back_populates="upload")


class Files(Base):
    __tablename__ = "files"

    id = Column(Integer, ForeignKey("uploads.id"), primary_key=True)
    pptx_file = Column("pptx_data", BLOB, nullable=True)

    # Relationships
    upload = relationship("Upload", back_populates="file")


this_path = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = "sqlite:///" + str(this_path) + "./excellenteam.db"
engine = create_engine(DATABASE_URL, echo=True)  # echo=True for better logging
#
# Create tables in the database
Base.metadata.create_all(bind=engine)
#
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ===================
# fUNCTIONS:
# ===================
def add_user(email: str) -> int:
    """
    @summary:
        Add a user to the database.
        if there is already a user with the same email, do nothing.
    @param email: str
        The email of the new user.
    @return: int
        The ID of the user.
    """
    session = SessionLocal()
    user = session.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email)
        session.add(user)
        session.commit()
        session.refresh(user)
    session.close()
    return user.id


def get_user_by_id(user_id: int) -> dict:
    """
    @summary:
        Get the user from the database by ID.
    @param user_id: int
        The ID of the user.
    @return: dict
        The user represented as a dictionary.
    @example:
        get_user_by_id(1) -> {"id": 1, "email": "user_email@xyz.com"}
    """
    session = SessionLocal()
    user = session.query(User).filter(User.id == user_id).first()
    session.close()

    if user:
        return {"id": user.id, "email": user.email}
    else:
        return None


def get_user_by_email(user_email:str) -> dict:
    """
    @summary:
        Get the user from the database by email.
    @param user_email: str
        The email of the user.
    @return: dict
        1st key-value: id of the user - int
        2nd key-value: email of the user - str
    """
    session = SessionLocal()
    user = session.query(User).filter(User.email == user_email).first()
    session.close()
    user_id = None
    email = None
    if user:
        user_id = user.id
        email = user.email
    return {"id": user_id, "email": email}


def add_new_pptx_file(filename: str, email: str = None) -> None:
    """
    @summary:
        Add a new pptx file to the database.
        if the email is not None, use the add_user function to add the user to the database.
    @param filename: str
        The name of the file.
    @param email: str
        The email of the user.
    """
    if email:
        user_id = add_user(email)
    else:
        user_id = None

    session = SessionLocal()
    upload_time = datetime.utcnow()
    status = "pending"

    # Read the PPTX file as binary data
    with open(filename, 'rb') as f:
        file_blob = f.read()

    # Insert the new Upload record
    new_upload = Upload(filename=filename, upload_time=upload_time, status=status, user_id=user_id)
    session.add(new_upload)
    session.commit()
    session.refresh(new_upload)

    # Get the ID of the newly created Upload record
    upload_id = new_upload.id

    # Insert the binary data to the Files table
    new_file = Files(id=upload_id, pptx_file=file_blob)
    session.add(new_file)

    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_pptx_file(id_file: int) -> bytes:
    """
    @summary:
        Get the binary data of the pptx file from the database.
    @param id_file: int
        The ID of the file.
    @return: bytes
        The binary data of the file.
    """
    session = SessionLocal()
    file = session.query(Files).filter(Files.id == id_file).first()
    session.close()
    return file.pptx_file


def convert_bytes_to_pptx_file(bytes_pptx_file: bytes, output_filename: str) -> None:
    """
    @summary:
        Convert the binary data of the pptx file to a file and save it to the current folder.
    @param bytes_pptx_file: bytes
        The binary data of the file.
    @param output_filename: str
        The name of the output file. This can include a directory path if desired.
    """
    with open(output_filename, 'wb') as f:
        f.write(bytes_pptx_file)


def get_pptx_bytes(file_id: int) -> bytes:
    """
    @summary:
        Get the binary data of the pptx file from the database.
    @param file_id: int
        The ID of the file.
    @return: bytes
        The binary data of the file.
    """
    session = SessionLocal()
    file = session.query(Files).filter(Files.id == file_id).first()
    session.close()
    return file.pptx_file


def insert_upload_explanation(id_upload: int, explanation: dict) -> None:
    """
    @summary:
        Insert the explanation of the upload to the database.
    @param id_upload: int
        The ID of the upload.
    @param explanation: dict
        The explanation of the upload.
    """
    session = SessionLocal()
    upload = session.query(Upload).filter(Upload.id == id_upload).first()
    upload.explanation = explanation
    session.commit()
    session.close()


# print(get_pptx_bytes(1))
