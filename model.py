from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, REAL
from passlib.apps import custom_app_context as pwd_context
engine = create_engine("sqlite:///db/begin.db", convert_unicode=True)
metadata = MetaData()
db_session = scoped_session(sessionmaker(autocommit=False,autoflush=False,bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()
class Trader(Base):
    __tablename__ = 'traders'
    id = Column(Integer, primary_key=True)
    id_pass = Column(Integer, unique=True, nullable=False)
    name = Column(String(50),unique=True)
    email = Column(String(150),unique=True)
    phone = Column(String(60), unique=True)
    county = Column(Integer)
    password = Column(String(128), nullable=False)
    livestocks = relationship("Livestock", back_populates="traders")
    profile_pic = Column(String(250), nullable=False,default="profiles/nopic.jpg")
    def __init__(self, name=None, email=None, county=1, id_pass=None, phone=None, password = None):
        self.name = name 
        self.email = email
        self.county = county
        self.id_pass = id_pass
        self.phone = phone
        self.password = password
    def hash_password(self, password):
        self.password = pwd_context.encrypt(password)
    def verify_password(self, password):
        return pwd_context.verify(self.password, password)
class Type(Base):
    __tablename__ = "types"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    default_image = Column(String(200), unique=True)
class Livestock(Base):
    __tablename__ = "livestocks"
    id = Column(Integer, primary_key=True)
    tag = Column(Integer, unique=True)
    type_id = Column(Integer, ForeignKey("types.id"))
    owner_id = Column(Integer, ForeignKey("traders.id"))
    traders = relationship("Trader")
    diagnosis = relationship("Diagnosis", back_populates="livestocks")
    medications = relationship("Medication", back_populates='livestocks')
    types = relationship("Type")
    profile_pic = Column(String(120), nullable=False)
class Diagnosis(Base):
    __tablename__ = "diagnosis"
    id = Column(Integer, primary_key=True)
    animal_id = Column(Integer, ForeignKey("livestocks.id"))
    visit_id = Column(Integer, ForeignKey("visits.id", ondelete="CASCADE"))
    disease_id = Column(Integer, ForeignKey("diseases.id"))
    livestocks = relationship("Livestock")
    visits = relationship("Visit", back_populates="diagnosis")
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
    #medication_id = Column(Integer, ForeignKey("medications.id"))
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
    def __init__(self):
        pass
class Symptom(Base):
    __tablename__ = "symptoms"
    id = Column(Integer, primary_key=True)
    description = Column(String(1000))
    disease_id = Column(Integer, ForeignKey("diseases.id"))
    diseases = relationship("Disease", back_populates="symptoms")
class County(Base):
    __tablename__ = "counties"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    def __init__(self, name=None):
        self.name = name

def init_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

#init_db()
