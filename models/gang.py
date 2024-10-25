from sqlalchemy import Column, Integer, String
from app import db
from error_handler import ErrorHandler
from marshmallow import  ValidationError
from models import Member

class Gang(db.Model):
    __tablename__ = 'Gang'

    gang_id = Column(Integer, primary_key=True)
    gang_name = Column(String, nullable=False)
    gang_description = Column(String)

    members = db.relationship("Member", back_populates="gang")

    @staticmethod
    def index():
        return Gang.query.all()

    @staticmethod
    def show(id):
        return Gang.query.get(id)

    @staticmethod
    def create(data):
        try:

            existing_gang = Gang.validation(data)
            gang = Gang(
                gang_name=existing_gang.get('gang_name'),
                gang_description=existing_gang.get('gang_description')
            )

            db.session.add(gang)
            db.session.commit()
            return {'success': True, 'message': 'Gang created successfully', 'gang_id': gang.gang_id}, 201
        except ValidationError as err:
            return ErrorHandler.handle_validation_error(err.messages)
        except Exception as e:
            return ErrorHandler.handle_error(str(e))

    @staticmethod
    def update(data, id):
        try:
            gang = Gang.show(id)
            gang.gang_name = data.get('gang_name', gang.gang_name)
            gang.gang_description = data.get('gang_description', gang.gang_description)
            db.session.commit()

            return {'success': True, 'message': 'Gang updated successfully', 'gang_id': gang.gang_id}, 200
        except Exception as e:
            return ErrorHandler.handle_error(str(e))

    @staticmethod
    def delete(id):
        try:
            gang = Gang.query.get(id)
            if not gang:
                return {'success': False, 'message': 'Gang not found'}, 404

            db.session.delete(gang)
            db.session.commit()
            return {'success': True, 'message': 'Gang deleted successfully'}, 200
        except Exception as e:
            return ErrorHandler.handle_error(str(e))

    @staticmethod
    def get_top_gangs(limit=5):
        return Gang.query \
            .join(Member, Member.gang_id == Gang.gang_id) \
            .group_by(Gang.gang_id, Gang.gang_name, Gang.gang_description) \
            .order_by(db.func.count(Member.member_id).desc()) \
            .limit(limit) \
            .all()

    @staticmethod
    def validation(data):
        existing_gang = Gang.query.filter_by(gang_name=data.get('gang_name')).first()
        if existing_gang:
            raise ValidationError("A gang with this name already exists.")
        return existing_gang


    def __repr__(self):
        return f"<Gang {self.gang_id}: {self.gang_name}>"
