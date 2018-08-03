from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, REAL, DateTime
from passlib.hash import pbkdf2_sha256
import datetime
engine = create_engine("sqlite:///db/begin.db", convert_unicode=True)
metadata = MetaData()
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


class Admin(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(50), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    fullnames = Column(String(100), nullable=False)
    password = Column(String(80), nullable=False)
    profile_pic = Column(String(50), nullable=False, default="/static/profiles/profile.png")

    def __init__(self, email, fullnames, username, password, profile_pic=None):
        self.email = email
        self.username = username
        self.password = password
        self.profile_pic = profile_pic
        self.fullnames = fullnames

    def hash_password(self):
        self.password = pbkdf2_sha256.hash(self.password)

    def verify_password(self, password):
        return pbkdf2_sha256.verify(password, self.password)


class Veterinary(Base):
    __tablename__ = "veterinaries"
    id = Column(Integer, primary_key=True)
    full_names = Column(String(150), nullable=False)
    username = Column(String(25), nullable=False, unique=True)
    password = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    county = Column(Integer, ForeignKey("counties.id"))
    national_id = Column(Integer, nullable=False, unique=True)
    phone = Column(String(15), nullable=False, unique=True)
    fromwhere = relationship('County', backref='veterinaries')
    added = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    status = Column(Integer, default=1, nullable=False)

    def __init__(self, full_names, username, password, email, county, national_id, phone, added=None, status= None):
        self.full_names = full_names
        self.username = username
        self.password = password
        self.email = email
        self.county = county
        self.phone = phone
        self.national_id = national_id
        self.added = added
        self.status = status

    def hash_password(self):
        self.password = pbkdf2_sha256.hash(self.password)

    def verify_password(self, password):
        return pbkdf2_sha256.verify(password, self.password)


class Trader(Base):
    __tablename__ = 'traders'
    id = Column(Integer, primary_key=True)
    id_pass = Column(Integer, unique=True, nullable=False)
    name = Column(String(50), unique=True)
    email = Column(String(150), unique=True)
    phone = Column(String(60), unique=True)
    bio = Column(String(500), nullable=False, default="No bio availbale")
    county = Column(Integer)
    password = Column(String(128), nullable=False)
    livestocks = relationship("Livestock", back_populates="traders")
    profile_pic = Column(String(250), nullable=False, default="/static/profiles/profile.jpg")

    def __init__(self, name=None, email=None, county=1, id_pass=None, phone=None, password=None, bio=None):
        self.name = name
        self.email = email
        self.county = county
        self.id_pass = id_pass
        self.phone = phone
        self.password = password
        self.bio = bio

    def hash_password(self):
        self.password = pbkdf2_sha256.hash(self.password)

    def verify_password(self, password):
        return pbkdf2_sha256.verify(password, self.password)


class Type(Base):
    __tablename__ = "types"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    default_image = Column(String(200), unique=True)
    def __init__(self, title):
        self.name = title


class Livestock(Base):
    __tablename__ = "livestocks"
    id = Column(Integer, primary_key=True)
    tag = Column(Integer, unique=True)
    type_id = Column(Integer, ForeignKey("types.id"))
    gender = Column(Integer, nullable=False)
    owner_id = Column(Integer, ForeignKey("traders.id"))
    traders = relationship("Trader")
    diagnosis = relationship("Diagnosis", back_populates="livestocks")
    medications = relationship("Medication", back_populates='livestocks')
    on_sale = Column(Integer, nullable=False, default=0)
    types = relationship("Type")
    profile_pic = Column(String(120), nullable=False)
    def __init__(self, tag, type_id, gender, owner_id):
        self.tag = tag
        self.type_id = type_id
        self.gender = gender
        self.owner_id = owner_id
        self.on_sale = 0

class Diagnosis(Base):
    __tablename__ = "diagnosis"
    id = Column(Integer, primary_key=True)
    animal_id = Column(Integer, ForeignKey("livestocks.id"))
    visit_id = Column(Integer, ForeignKey("visits.id", ondelete="CASCADE"))
    disease_id = Column(Integer, ForeignKey("diseases.id"))
    livestocks = relationship("Livestock")
    visits = relationship("Visit", back_populates="diagnosis")
    def __init__(self, animal_id, visit_id, disease_id):
        self.animal_id = animal_id
        self.visit_id = visit_id
        self.disease_id = disease_id


class Visit(Base):
    __tablename__ = "visits"
    id = Column(Integer, primary_key=True)
    diagnosis = relationship("Diagnosis", back_populates="visits")

class Disease(Base):
    __tablename__ = 'diseases'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    effect = Column(REAL, unique=False, default=1.0)
    symptoms = relationship("Symptom", back_populates="diseases")
    # medication_id = Column(Integer, ForeignKey("medications.id"))
    medications = relationship("Medication", back_populates="diseases")
    def __init__(self, name=None, effect=None):
        self.effect = effect
        self.name = name


class Medication(Base):
    __tablename__ = 'medications'
    id = Column(Integer, primary_key=True)
    name = Column(String(60), unique=True)
    disease_id = Column(Integer, ForeignKey("diseases.id"))
    livestock_id = Column(Integer, ForeignKey("livestocks.id"))
    diseases = relationship("Disease", back_populates="medications")
    livestocks = relationship("Livestock", back_populates="medications")

    def __init__(self, name, disease_id, livestock_id):
        self.name = name
        self.disease_id = disease_id
        self.livestock_id = livestock_id


class Symptom(Base):
    __tablename__ = "symptoms"
    id = Column(Integer, primary_key=True)
    description = Column(String(1000))
    disease_id = Column(Integer, ForeignKey("diseases.id"))
    diseases = relationship("Disease", back_populates="symptoms")
    def __init__(self, description, disease_id):
        self.description = description
        self.disease_id = disease_id

class County(Base):
    __tablename__ = "counties"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __init__(self, name=None):
        self.name = name


def init_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

# init_db()
