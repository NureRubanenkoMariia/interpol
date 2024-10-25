from sqlalchemy import Column, Integer, String, Date, ForeignKey, Computed
from error_handler import ErrorHandler
from marshmallow import Schema, fields, validate, ValidationError
from request.member_request import MemberSchema

from app import db

class Member(db.Model):
    __tablename__ = 'Member'

    member_id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    alias = Column(String)
    date_of_birth = Column(Date, nullable=False)
    sex = Column(String(6), nullable=False)
    age = Column(Integer, Computed("(datediff(year, [Date_of_birth], getdate()))"), nullable=True)
    threat_level = Column(Integer, nullable=False)
    gang_id = Column(Integer, ForeignKey('Gang.gang_id'))
    country_id = Column(Integer, ForeignKey('Country.country_id'))
    gang = db.relationship("Gang", back_populates="members")
    country = db.relationship("Country", back_populates="members")

    @staticmethod
    def index():
        return Member.query.order_by(Member.member_id.desc()).all()

    @staticmethod
    def show(id):
        return Member.query.get(id)

    @staticmethod
    def create(data):
        try:
            validated_data = Member.validation(data)

            member = Member(
                first_name=validated_data.get('first_name'),
                last_name=validated_data.get('last_name'),
                alias=validated_data.get('alias'),
                date_of_birth=validated_data.get('date_of_birth'),
                sex=validated_data.get('sex'),
                # age=validated_data.get('age'),
                threat_level=validated_data.get('threat_level'),
                gang_id=validated_data.get('gang_id'),
                country_id=validated_data.get('country_id')
            )
            db.session.add(member)
            db.session.commit()

            return {'success': True, 'message': 'Member created successfully', 'member_id': member.member_id}, 201
        except ValidationError as err:
            return ErrorHandler.handle_validation_error(err.messages)
        except Exception as e:
            return ErrorHandler.handle_error(str(e))

    @staticmethod
    def get_member_gang(gang_id):
        return Member.query.filter_by(gang_id=gang_id).all()

    @staticmethod
    def delete(id):
        try:
            member = Member.query.get(id)
            db.session.delete(member)
            db.session.commit()
            return {'success': True, 'message': 'Member deleted successfully'}, 200
        except Exception as e:
            return ErrorHandler.handle_error(str(e))

    @staticmethod
    def update(data, id):
        try:
            member = Member.query.get(id)
            if not member:
                return {'success': False, 'message': 'Member not found'}, 404

            validated_data = MemberSchema().load(data)
            member.first_name = validated_data.get('first_name')
            member.last_name = validated_data.get('last_name')
            member.alias = validated_data.get('alias')
            member.date_of_birth = validated_data.get('date_of_birth')
            member.sex = validated_data.get('sex')
            member.threat_level = validated_data.get('threat_level')
            member.gang_id = validated_data.get('gang_id')
            member.country_id = validated_data.get('country_id')

            db.session.commit()

            return {'success': True, 'message': 'Member updated successfully',
                    'member_id': member.member_id}, 200
        except ValidationError as err:
            return ErrorHandler.handle_validation_error(err.messages)
        except Exception as e:
            return ErrorHandler.handle_error(str(e))


    @staticmethod
    def validation(data):
        schema = MemberSchema()
        try:
            validated_data = schema.load(data)
            return validated_data
        except ValidationError as err:
            raise ValidationError(err.messages)

    def __repr__(self):
        return f"<Member {self.member_id}: {self.first_name} {self.last_name}>"
