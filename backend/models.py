# models.py
import time
from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String
from database import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

     # link to datasets
    datasets = relationship("Dataset", back_populates="owner")
     # Add relationships for all models
    linear_regression_models = relationship("LinearRegressionModel", back_populates="user")
    logistic_regression_models = relationship("LogisticRegressionModel", back_populates="user")
    decision_tree_models = relationship("DecisionTreeModel", back_populates="user")
    bagging_models = relationship("BaggingModel", back_populates="user")
    boosting_models = relationship("BoostingModel", back_populates="user")
    random_forest_models = relationship("RandomForestModel", back_populates="user")
    svm_models = relationship("SVMModel", back_populates="user")
    user_defined_dnn_models = relationship("UserDefinedDNNModel", back_populates="user")

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="datasets")



class LinearRegressionModel(Base):
    __tablename__ = "linear_regression_models"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    dataset = Column(String, index=True)
    parameters = Column(JSON)  # store model parameters if needed
    metrics = Column(JSON)     # store performance metrics
    created_at = Column(DateTime, default=time.time())

    user = relationship("User", back_populates="linear_regression_models")


class LogisticRegressionModel(Base):
    __tablename__ = "logistic_regression_models"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    dataset = Column(String, index=True)
    parameters = Column(JSON)
    metrics = Column(JSON)
    created_at = Column(DateTime, default=time.time())

    user = relationship("User", back_populates="logistic_regression_models")


class DecisionTreeModel(Base):
    __tablename__ = "decision_tree_models"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    dataset = Column(String, index=True)
    parameters = Column(JSON)
    metrics = Column(JSON)
    created_at = Column(DateTime, default=time.time())

    user = relationship("User", back_populates="decision_tree_models")


class BaggingModel(Base):
    __tablename__ = "bagging_models"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    dataset = Column(String, index=True)
    parameters = Column(JSON)
    metrics = Column(JSON)
    created_at = Column(DateTime, default=time.time())

    user = relationship("User", back_populates="bagging_models")


class BoostingModel(Base):
    __tablename__ = "boosting_models"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    dataset = Column(String, index=True)
    parameters = Column(JSON)
    metrics = Column(JSON)
    created_at = Column(DateTime, default=time.time())

    user = relationship("User", back_populates="boosting_models")


class RandomForestModel(Base):
    __tablename__ = "random_forest_models"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    dataset = Column(String, index=True)
    parameters = Column(JSON)
    metrics = Column(JSON)
    created_at = Column(DateTime, default=time.time())

    user = relationship("User", back_populates="random_forest_models")


class SVMModel(Base):
    __tablename__ = "svm_models"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    dataset = Column(String, index=True)
    parameters = Column(JSON)
    metrics = Column(JSON)
    created_at = Column(DateTime, default=time.time())

    user = relationship("User", back_populates="svm_models")


class UserDefinedDNNModel(Base):
    __tablename__ = "user_defined_dnn_models"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    dataset = Column(String, index=True)
    parameters = Column(JSON)
    metrics = Column(JSON)
    created_at = Column(DateTime, default=time.time())

    user = relationship("User", back_populates="user_defined_dnn_models")
