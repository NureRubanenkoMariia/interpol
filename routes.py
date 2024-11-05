from flask import render_template, request, redirect, jsonify
from error_handler import ErrorHandler
from models import Member, Gang, Country


def init_routes(app, db):

    @app.route('/')
    @app.route('/home')
    def index():
        return render_template("index.html")


    @app.route('/about')
    def about():
        return render_template("about.html")


    @app.route('/member/<int:id>')
    def member_detail(id):
        member = Member.show(id)
        gang = Gang.show(member.gang_id) if member.gang_id else None
        country = Country.show(member.country_id) if member.country_id else None
        return render_template("member_detail.html", member=member, gang=gang, country=country)

    @app.route('/members')
    def members():
        members = Member.index()
        return render_template("members.html", members=members)

    @app.route('/member/delete/<int:id>',methods=['DELETE'])
    def member_delete(id):
        response, status_code = Member.delete(id)
        return response, status_code


    @app.route('/member/update/<int:id>', methods=['PUT', 'GET'])
    def member_update(id):
        member = Member.show(id)
        gangs = Gang.index()
        countries = Country.index()
        if request.method == 'PUT':
            if request.is_json:
                data = request.get_json()
                response, status_code = Member.update(data, id)
                return response, status_code
            else:
                return jsonify({"error": "Request must be JSON"}), 400

        return render_template("member_update.html", member=member, gangs=gangs, countries=countries)



    @app.route('/create_member', methods=['GET', 'POST'])
    def create_member():
        gangs = Gang.index()
        countries = Country.index()
        if request.method == 'POST':
            if request.is_json:
                data = request.get_json()
                response, status_code = Member.create(data)
                return response, status_code
            else:
                response = {'error': 'Request must be JSON'}
                return jsonify(response), 400
        else:
            return render_template('create_member.html', gangs=gangs, countries=countries)

    @app.route('/gangs')
    def gangs():
        gangs = Gang.index()
        return render_template('gangs.html', gangs=gangs)

    @app.route('/gang_detail/<int:gang_id>')
    def gang_detail(gang_id):
        gang = Gang.show(gang_id)
        members = Member.get_member_gang(gang_id)
        return render_template('gang_detail.html', gang=gang, members=members)

    @app.route('/gang/delete/<int:id>',methods=['DELETE'])
    def gang_delete(id):
        response, status_code = Gang.delete(id)
        return response, status_code

    @app.route('/create_country', methods=[ 'POST'])
    def create_country():
            if request.is_json:
                data = request.get_json()
                response, status_code = Country.create(data)
                return response, status_code
            else:
                response = {'error': 'Request must be JSON'}
                return jsonify(response), 400

    @app.route('/create_gang', methods=[ 'POST'])
    def create_gang():
            if request.is_json:
                data = request.get_json()
                response, status_code = Gang.create(data)
                return response, status_code
            else:
                response = {'error': 'Request must be JSON'}
                return jsonify(response), 400

    @app.route('/gang/update/<int:id>', methods=['PUT'])
    def gang_update(id):
                data = request.get_json()
                response, status_code = Gang.update(data, id)
                return response, status_code


    @app.route('/statistic')
    def statistics():
        top_gangs = Gang.get_top_gangs()
        top_countries = Country.get_top_countries()

        return render_template("statistic.html", top_gangs=top_gangs, top_countries=top_countries)

    @app.route('/count_criminals', methods=['GET', 'POST'])
    def count_criminals():
        gangs = Gang.index()
        if request.method == 'POST':
            data = request.get_json()
            gang_name = data.get('gang_name')
            min_search_count = data.get('min_search_count')
            return Member.count_criminals_in_gang(gang_name, min_search_count)
        else:
            return render_template('count_criminals.html', gangs=gangs)


    @app.route('/total_search_records', methods=['GET', 'POST'])
    def total_search_records():
        members = Member.index()
        if request.method == 'POST':
            member_id = request.form.get('member_id')
            return Member.get_total_search_records(member_id)

        return render_template('total_search.html', members=members)


    @app.route('/gang_info', methods=['GET', 'POST'])
    def gang_info():
        if request.method == 'POST':
            data = request.get_json()
            gang_name = data.get('gang_name')
            return Member.update_and_get_gang_members(gang_name)
        else:
            gangs = Gang.index()
            return render_template('gang_info.html', gangs=gangs)

