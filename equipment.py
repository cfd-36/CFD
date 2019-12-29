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
	</ul>
    </body>
</html>
'''.format()
        elif base == "truck-check":
            db = MySQLdb.connect(host="localhost", user="jdike", passwd="",
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
            notes = args["notes"][0]

            update_sql = ("insert into readiness_history set equipment = %s, " +
                          "location = %s, check_desc = %s, " +
                          "time = from_unixtime(%s), ok = %s, notes = %s, " +
                          "who = %s")
            update = ("insert into readiness_history set equipment = {0}, " +
                      "location = {1}, check_desc = {2}, " +
                      "time = from_unixtime({3}), ok = {4}, notes = {5}, " +
                      "who = {6}")
            print(update.format(equipment, location, check,
                                int(datetime.now().timestamp()), int(ok),
                                notes, "36"))

            db = MySQLdb.connect(host="localhost", user="jdike", passwd="",
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
