# save this as app.py
from flask import Flask, render_template_string
import folium
import csv
from folium.plugins import MarkerCluster
app = Flask(__name__)

@app.route("/")
def hello():
    #creates the map
    filename = "EastTennesseeTest.csv"
    keys = ('Name','Age','Race','Gender','Coordinates','Occupation','Crime','Method','Death','County','Source1','Source2','Source3')
    records = []
    #read the data from the CSV file into our Python app
    with open(filename, 'r', encoding='latin-1') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            records.append({key: row[key] for key in keys})
    #Unpacking records
    for record in records:
        coordinates = record['Coordinates']
    
        # Check if the 'Coordinates' field contains expected format
        if "(" in coordinates and ")" in coordinates:
            # Extract the portion within parentheses and then split it into latitude and longitude
            coord_part = coordinates.split("(")[-1].split(')')[0]
            latitude, longitude = coord_part.split()
            record['longitude'] = float(longitude)
            record['latitude'] = float(latitude)
        else:
            # Handle cases where the 'Coordinates' format is not as expected
            record['longitude'] = None
            record['latitude'] = None
    
    #Coords of the map
    mapObj = folium.Map(location=[36.1691287, -86.7847898], zoom_start=6)
    
    
    # Filter out records with missing or invalid coordinates
    valid_records = [record for record in records if record.get('latitude') is not None and record.get('longitude') is not None]

    # Create a MarkerCluster group
    marker_cluster = MarkerCluster().add_to(mapObj)

    # Add markers to the MarkerCluster group
    for record in valid_records:
        coord = (record['latitude'], record['longitude'])
        
        # Create a pop-up label with multiple fields
        popup_text = f"Name: {record.get('Name', 'N/A')}<br>Age: {record.get('Age', 'N/A')}<br>Race:{record.get('Race', 'N/A')} {record.get('Gender', 'N/A')}<br>Occupation: {record.get('Occupation', 'N/A')}<br>Crime: {record.get('Crime', 'N/A')}<br>Method: {record.get('Method', 'N/A')}<br>Death: {record.get('Death', 'N/A')}<br>County: {record.get('County', 'N/A')}<br>Source1: {record.get('Source1', 'N/A')}<br>Source2: {record.get('Source2', 'N/A')}<br>Source3: {record.get('Source3', 'N/A')}"
        
        marker = folium.Marker(location=coord, popup=popup_text)
        marker.add_to(marker_cluster)
        
    # Add the Counties.geojson as a layer to the map
    counties_layer = folium.GeoJson("Counties.geojson", name="Counties Layer")
    
    def add_hover_popup(feature, layer):
        properties = feature['properties']
        name = properties.get('NAMESLAD')  # Replace 'NAMELSAD' with the actual property name in your GeoJSON
        layer.bind_tooltip(name)

# Apply the custom function to each feature in the GeoJSON layer
    counties_layer.add_child(folium.GeoJsonTooltip(fields=['County:']))
    counties_layer.add_to(mapObj)
   
    

    # Create a layer control to toggle between the marker cluster and Counties.geojson layers
    folium.LayerControl().add_to(mapObj)
    #renders the map 
    mapObj.get_root().render()
    
    #renders to html
    header = mapObj.get_root().header.render()
    #
    body_html = mapObj.get_root().html.render()
    #Java script render
    script =  mapObj.get_root().script.render()
    return render_template_string( """
    <!DOCTYPE html>
    <html>
        <head>
        {{header|safe}}
        </head>
        <body>
            <h3>State of Tennessee Death Penalty Map </h3>
            {{body_html|safe}}
            
            <script>
            {{script|safe}}
            </script>
        </body>
    </htm>

    """, header=header, body_html=body_html, script=script)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=50100,debug=True)
