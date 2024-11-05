from sqlalchemy import Column, Integer, String, Date, ForeignKey, Computed
from error_handler import ErrorHandler
from marshmallow import Schema, fields, validate, ValidationError
from request.member_request import MemberSchema
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from flask import jsonify

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
            db.session.rollback()
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
    def count_criminals_in_gang(gang_name, min_search_count):
        try:
            query = text("SELECT * FROM dbo.CountCriminalsInGang(:gang_name, :min_search_count)")
            result = db.session.execute(query,
                                        {'gang_name': gang_name, 'min_search_count': min_search_count}).fetchall()

            if result:
                criminals = [{'member_name': row.member_name, 'search_count': row.search_count} for row in result]
                return jsonify({"criminals": criminals})
            else:
                return jsonify({"message": "No data found"})

        except Exception as e:
            return ErrorHandler.handle_error(str(e))

    @staticmethod
    def get_total_search_records(member_id):
        try:
            query = text("SELECT dbo.GetTotalSearchRecords(:member_id) AS total_count")
            result = db.session.execute(query, {'member_id': member_id}).scalar()
            return jsonify({"total_count": result})

        except Exception as e:
            return ErrorHandler.handle_error(str(e))


    @staticmethod
    def update_and_get_gang_members(gang_name):
        try:
            update_query = text("EXEC UpdateCriminalsThreatLevelDescription :gang_name")
            db.session.execute(update_query, {'gang_name': gang_name})
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            error = str(e.__dict__['orig'])
            if '50001' in error:
                return jsonify({"members": [], "error": "Інформація відсутня для вказаної банди"}), 404
            return jsonify({"members": [], "error": "Помилка під час оновлення даних"}), 500

        query = """
            SELECT first_name, threat_level, sings_description
            FROM gang
            JOIN member ON member.gang_id = gang.gang_id
            JOIN personal_sings ON member.member_id = personal_sings.member_id
            WHERE gang_name = :gang_name
            ORDER BY threat_level DESC
        """
        members = db.session.execute(text(query), {'gang_name': gang_name}).fetchall()
        members_data = [
            {
                "first_name": row.first_name,
                "threat_level": row.threat_level,
                "sings_description": row.sings_description
            } for row in members
        ]
        return jsonify({"members": members_data})

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
