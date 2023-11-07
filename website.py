# save this as app.py
from flask import Flask, render_template_string
import folium
import csv
from folium.plugins import MarkerCluster
import os
app = Flask(__name__)

@app.route("/")
def hello():
    #creates the map
    filename = "MasterMap.csv"
    
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
    marker_cluster = MarkerCluster(name="Points of Cases").add_to(map)


    # Add markers to the MarkerCluster group
    for record in valid_records:
        coord = (record['latitude'], record['longitude'])

        # Create a pop-up label with multiple fields and conditionally include source links
        popup_text = f"Name: {record.get('Name', '?')}<br>Age: {record.get('Age', '?')}<br>Race:{record.get('Race', '?')} {record.get('Gender', '?')}<br>Occupation: {record.get('Occupation', '?')}<br>Crime: {record.get('Crime', '?')}<br>Method: {record.get('Method', '?')}<br>Death: {record.get('Death', '?')}<br>County: {record.get('County', '?')}<br>"

         # Check for source links and add them to the pop-up if available
        source_links = []

        if 'Source1' in record and record['Source1']:
            source_links.append(f"<a href='{record['Source1']}' target='_blank'>Source 1</a>")

        if 'Source2' in record and record['Source2']:
            source_links.append(f"<a href='{record['Source2']}' target='_blank'>Source 2</a>")

        if 'Source3' in record and record['Source3']:
            source_links.append(f"<a href='{record['Source3']}' target='_blank'>Source 3</a>")

        if source_links:
            popup_text += "<br>".join(source_links)

        if popup_text:
            popup_text += "<br>"


        marker = folium.Marker(location=coord, popup=folium.Popup(popup_text, max_width=300))
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
    #Map render
    body_html = mapObj.get_root().html.render()
    #Java script render
    script =  mapObj.get_root().script.render()
    

    #Website render
    return render_template_string( """
    <!DOCTYPE html>
    <html>
        <head>
        {{header|safe}}
        </head>
        <body>
            <h3>State of Tennessee Death Penalty Map </h3>
            <!--Map Size -->
            <div id="map-container" style="width: 80%; height: 800px; margin: 20px auto;">
            {{body_html|safe}} <!-- Map Render -->
             </div>
            
            <script>
            {{script|safe}}
            </script>
        </body>
    </htm>

    """, header=header, body_html=body_html, script=script)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80800,debug=True)
