from sqlalchemy import Column, Integer, String
from app import db
from error_handler import ErrorHandler
from marshmallow import Schema, fields, validate, ValidationError
from models import Member

class Country(db.Model):
    __tablename__ = 'Country'

    country_id = Column(Integer, primary_key=True)
    country_name = Column(String, nullable=False)
    members = db.relationship("Member", back_populates="country")

    @staticmethod
    def index():
        return Country.query.all()

    @staticmethod
    def show(id):
        return Country.query.get(id)

    @staticmethod
    def create(data):
        try:

            existing_country = Country.validation(data)
            country = Country(
                country_name=data.get('country_name'),
            )
            db.session.add(country)
            db.session.commit()
            return {'success': True, 'message': 'Country created successfully', 'country_id': country.country_id}, 201
        except ValidationError as err:
            return ErrorHandler.handle_validation_error(err.messages)
        except Exception as e:
            return ErrorHandler.handle_error(str(e))

    @staticmethod
    def update(data, id):
        try:
            country = Country.query.get(id)
            if not country:
                return {'success': False, 'message': 'Country not found'}, 404

            country.country_name = data.get('country_name', country.country_name)
            db.session.commit()

            return {'success': True, 'message': 'Country updated successfully', 'country_id': country.country_id}, 200
        except ValidationError as err:
            return ErrorHandler.handle_validation_error(err.messages)
        except Exception as e:
            return ErrorHandler.handle_error(str(e))

    @staticmethod
    def delete(id):
        try:
            country = Country.query.get(id)
            if not country:
                return {'success': False, 'message': 'Country not found'}, 404

            db.session.delete(country)
            db.session.commit()
            return {'success': True, 'message': 'Country deleted successfully'}, 200
        except Exception as e:
            return ErrorHandler.handle_error(str(e))

    @staticmethod
    def get_top_countries(limit=5):
        return Country.query \
            .join(Member, Member.country_id == Country.country_id) \
            .group_by(Country.country_id, Country.country_name) \
            .order_by(db.func.count(Member.member_id).desc()) \
            .limit(limit) \
            .all()

    @staticmethod
    def validation(data):
        existing_gang = Country.query.filter_by(country_name=data.get('country_name')).first()
        if existing_gang:
            raise ValidationError("A country with this name already exists.")
        return existing_gang

    def __repr__(self):
        return f"<Country {self.country_id}: {self.country_name}>"
