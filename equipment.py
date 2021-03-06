from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from urllib.parse import urlparse
from urllib.parse import parse_qs
from datetime import datetime
import MySQLdb

class CFDRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print("do_GET")
        url = urlparse(self.path)
        base = url.path[1:]
        args = parse_qs(url.query)
        if base == "":
            html = '''
<html>
    <head>
	<title>Where to go from here</title>
    </head>
    <body>
        <ul>
            <li><a href="truck-check">Check a truck</a></li>
            <li><a href="failed-readiness">Failed readiness checks</a></li>
            <li><a href="last-truck-check">Most recent truck checks</a></li>
	</ul>
    </body>
</html>
'''.format()
        elif base == "truck-check":
            db = MySQLdb.connect(host="localhost", user="CFD", passwd="",
                                 db="CFD")
            db.autocommit(True)
            cur = db.cursor()
            present_sql = ("select id from readiness_checks where " +
                           "equipment is NULL")
            cur.execute(present_sql)
            present_id = cur.fetchone()[0]
            if "truck" in args:
                truck = args['truck'][0]
                e_sql = ("select e.id, e.name, loc.compartment, loc.shelf, " +
                         "loc.id from locations as loc, equipment as e, " +
                         "equipment_location as el where " +
                         "loc.truck = '{0}' and loc.id = el.location and " +
                         "el.equipment = e.id order by " +
                         "loc.compartment, loc.shelf")
                cur.execute(e_sql.format(truck))
                e = cur.fetchall()

                rc_sql = ("select e.id, rc.check_desc, rc.id from " +
                          "equipment as e, readiness_checks as rc, " +
                          "equipment_location as el, locations as loc where " +
                          "loc.truck = '{0}' and el.location = loc.id and " +
                          "el.equipment = e.id and el.equipment = e.id")
                cur.execute(rc_sql.format(truck))
                rc = cur.fetchall()
                rc_by_id = { }
                for check in rc:
                    if not check[0] in rc_by_id:
                        rc_by_id[check] = [ ]
                    rc_by_id[check].append({ "description" : check[1],
                                             "id" : check[2] })

                rows = [ ]
                for equipment in e:
                    id = equipment[0]
                    if id in rc_by_id:
                        checks = rc_by_id[id]
                    else:
                        checks = [ { "name" : "", "id" : present_id } ]
                    check = checks.pop(0)
                    s = '''
<tr id={7}>
    <td>{0}</td>
    <td>{1}</td>
    <td>{2}</td>
    <td>{3}</td>
    <td>
	<input id={8} type='text'>
    </td>
    <td>
        <select onchange="javascript:update(this, {4}, {5}, {6}, '{7}', '{8}')">
	    <option value="-1">---</option>
	    <option value="1">Yes</option>
	    <option value="0">No</option>
	</select>
    </td>
</tr>'''
                    rows.append(s.format(equipment[2], equipment[3],
                                         equipment[1], check['name'], id,
                                         check["id"], equipment[4],
                                         "row-{0}".format(len(rows)),
                                         "notes-{0}".format(len(rows))))
                    for check in checks:
                        rows.append(s.format("", "", "", check,
                                             "row-{0}".format(len(rows))))
                html = '''
<html>
    <script>
function update(option, equip_id, check_id, loc_id, row_id, notes_id){{
    let ok = option.value;
    let xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function(){{
        if((xmlhttp.readyState == 4) && (xmlhttp.status == 200)){{
            let response = xmlhttp.responseText;
            let row = document.getElementById(row_id);
            if(response == "-1")
                color = "white"
            else if(response == "0")
                color = "LightSalmon"
            else if(response == "1")
                color = "PaleGreen"
            row.style.backgroundColor = color;
	}}
    }};
    let notes = document.getElementById(notes_id);
    xmlhttp.open("GET", "/update-check?ok=" + ok + "&equipment=" + equip_id +
		 "&location=" + loc_id + "&check=" + check_id + "&notes=" +
                 notes.value, true);
    xmlhttp.send();
}}
    </script>
    <head>
	<title>{0} Check</title>
    </head>
    <body>
	<table border="1">
	    <tr>
		<th>Compartment</th>
		<th>Shelf</th>
		<th>Equipment</th>
		<th>Check</th>
		<th>Notes</th>
		<th>OK</th>
	    </tr>
	    {1}
	</table>
    </body>
</html>
'''.format(truck, "".join(rows))
            else:
                trucks_sql = ("select distinct(truck) from locations")
                cur.execute(trucks_sql)
                trucks = cur.fetchall()
                truck_str = "<li><a href='?truck={0}'>{0}</a></li>"
                trucks_html = "".join([ truck_str.format(t[0])
                                        for t in trucks ])
                html = '''
<html>
    <head>
	<title>Check a truck</title>
    </head>
    <body>
        Choose a truck:
	<ul>
            {0}
	</ul>
    </body>
</html>
'''.format(trucks_html)
        elif base == "update-check":
            location = args["location"][0]
            equipment = args["equipment"][0]
            check = args["check"][0]
            ok = args["ok"][0]
            if "notes" in args:
                notes = args["notes"][0]
            else:
                notes = ""

            update_sql = ("insert into readiness_history set equipment = %s, " +
                          "location = %s, check_id = %s, " +
                          "time = from_unixtime(%s), ok = %s, notes = %s, " +
                          "who = %s")

            db = MySQLdb.connect(host="localhost", user="CFD", passwd="",
                                 db="CFD")
            db.autocommit(True)
            cur = db.cursor()
            cur.execute(update_sql, (equipment, location, check,
                                     int(datetime.now().timestamp()), int(ok),
                                     notes, "36"))

            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(ok.encode())
            return
        elif base == "failed-readiness":
            db = MySQLdb.connect(host="localhost", user="CFD", passwd="",
                                 db="CFD")
            db.autocommit(True)
            cur = db.cursor()
            cur.execute("select e.name, loc.truck, loc.compartment, " +
                        "loc.shelf, rc.check_desc, rh.time, rh.who, rh.notes " +
                        "from equipment as e, locations as loc, " +
                        "readiness_checks as rc, readiness_history as rh " +
                        "where rh.equipment = e.id and rh.location = loc.id " +
                        "and rc.id = rh.check_id")
            failed = cur.fetchall()
            rows = [ '''
<tr>
    <th>Equipment</th>
    <th>Check Failed</th>
    <th>When</th>
    <th>Truck</th>
    <th>Compartment</th>
    <th>Shelf</th>
    <th>Notes</th>
    <th>Noted By</th>
</tr>
''' ]
            for fail in failed:
                check = fail[4]
                if check == "":
                    check = "Present"
                rows.append('''
<tr>
    <td>{0}</td>
    <td>{1}</td>
    <td>{2}</td>
    <td>{3}</td>
    <td>{4}</td>
    <td>{5}</td>
    <td>{6}</td>
    <td>{7}</td>
</tr>
'''.format(fail[0], check, fail[5], fail[1], fail[2], fail[3], fail[7],
           fail[6]))
            html = '''
<html>
    <head>
	<title>Failed checks</title>
    </head>
    <body>
        <table border="1">
{0}
	</table>
    </body>
</html>
'''.format("\n".join(rows))
            pass
        elif base == "last-truck-check":
            db = MySQLdb.connect(host="localhost", user="CFD", passwd="",
                                 db="CFD")
            db.autocommit(True)
            cur = db.cursor()
            cur.execute("select max(rh.time), rh.who, loc.truck from " +
                        "readiness_history as rh, locations as loc " +
                        "group by loc.truck");
            checks = cur.fetchall()
            rows = [ '''
<tr>
    <th>Truck</th>
    <th>Last Checked</th>
    <th>By</th>
</tr>
''' ]
            for check in checks:
                rows.append('''
<tr>
    <td>{0}</td>
    <td>{1}</td>
    <td>{2}</td>
</tr>
'''.format(check[2], check[0], check[1]))
            html = '''
<html>
    <head>
	<title>Most recent truck checks</title>
    </head>
    <body>
        <table border="1">
{0}
	</table>
    </body>
</html>
'''.format("\n".join(rows))
        else:
            html = '''
<html>
    <head>
	<title>No such URL</title>
    </head>
    <body>
	<h1>URL : {0}</h1>
    </body>
</html>
'''.format(url.geturl())

        self.send_response(200)
        self.end_headers()
        self.wfile.write(html.encode())

server_address = ('', 8000)
httpd = HTTPServer(server_address, CFDRequestHandler)
httpd.serve_forever()
