#!/usr/bin/env python

from pyvis.network import Network
import base64
import os

# Function to read and encode image files into Base64 data URIs
def get_base64_image(image_path):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file '{image_path}' not found.")
    with open(image_path, 'rb') as img_file:
        data = img_file.read()
        base64_data = base64.b64encode(data).decode('utf-8')
        if image_path.lower().endswith('.png'):
            mime_type = 'image/png'
        elif image_path.lower().endswith('.svg'):
            mime_type = 'image/svg+xml'
        else:
            mime_type = 'image/png'
        data_uri = f'data:{mime_type};base64,{base64_data}'
        return data_uri

# Paths to your image files
router_image_path = 'router.png'
switch1_image_path = 'switch1.svg'
switch2_image_path = 'switch2.png'
optical_image_path = 'optical.png'

# Base64-encode your images
try:
    b64_router = get_base64_image(router_image_path)
    b64_switch1 = get_base64_image(switch1_image_path)
    b64_switch2 = get_base64_image(switch2_image_path)
    b64_optical = get_base64_image(optical_image_path)
except FileNotFoundError as e:
    print(e)
    exit(1)

# Initialize Pyvis network with a reasonable canvas size
net = Network(height='800px', width='100%', directed=False, layout=False)

# Disable physics to keep nodes in fixed positions initially
net.toggle_physics(False)

# Define canvas dimensions (adjust as needed for spacing)
canvas_width = 5000   # Half-width from center
canvas_height = 4000  # Half-height from center

# Add main device nodes with explicit positions and adjusted sizes
# Top-left corner: Router
net.add_node(
    "Router",
    label="Router",
    shape="image",
    image=b64_router,
    size=533,  # Reduced size by 1.5 times from 800
    title="Router - Handles network traffic",
    x=-canvas_width,
    y=-canvas_height,
    fixed=False,  # Allow dragging
    font={'size': 240, 'color': '#000000', 'strokeWidth': 0, 'align': 'center'}
)

# Top-right corner: Switch 2
net.add_node(
    "Switch 2",
    label="Switch 2",
    shape="image",
    image=b64_switch2,
    size=533,  # Reduced size by 1.5 times from 800
    title="Switch 2 - Backup switch",
    x=canvas_width,
    y=-canvas_height,
    fixed=False,  # Allow dragging
    font={'size': 240, 'color': '#000000', 'strokeWidth': 0, 'align': 'center'}
)

# Bottom-left corner: Switch 1
net.add_node(
    "Switch 1",
    label="Switch 1",
    shape="image",
    image=b64_switch1,
    size=533,  # Reduced size by 1.5 times from 800
    title="Switch 1 - Connected to Router",
    x=-canvas_width,
    y=canvas_height,
    fixed=False,  # Allow dragging
    font={'size': 240, 'color': '#000000', 'strokeWidth': 0, 'align': 'center'}
)

# Add edges between devices with adjusted widths (Removed labels to prevent duplication)
net.add_edge("Router", "Switch 1", color="black", width=30)
net.add_edge("Router", "Switch 2", color="black", width=30)
net.add_edge("Switch 1", "Switch 2", color="black", width=30)

# Add optical nodes connected to devices with adjusted sizes
optical_nodes = ['Optical Link 1', 'Optical Link 2', 'Optical Link 3']
for optical_node in optical_nodes:
    net.add_node(
        optical_node,
        shape="image",
        image=b64_optical,
        size=200,
        title="Optical Link",
        x=0,
        y=0,
        fixed=True,
        hidden=True
    )

# Add invisible edges from optical nodes to devices
optical_edges = [
    ('Optical Link 1', 'Router'),
    ('Optical Link 1', 'Switch 1'),
    ('Optical Link 2', 'Router'),
    ('Optical Link 2', 'Switch 2'),
    ('Optical Link 3', 'Switch 1'),
    ('Optical Link 3', 'Switch 2'),
]
for source, target in optical_edges:
    net.add_edge(source, target, hidden=True)

# Add label nodes for edge labels at 1/4 of the link length with increased font sizes
label_nodes_info = [
    {'id': 'Label Node 1', 'label': '5 Gbps', 'nodes': ['Router', 'Switch 1']},
    {'id': 'Label Node 2', 'label': '10 Gbps', 'nodes': ['Router', 'Switch 2']},
    {'id': 'Label Node 3', 'label': '1 Gbps', 'nodes': ['Switch 1', 'Switch 2']},
]

for ln in label_nodes_info:
    net.add_node(
        ln['id'],
        label=ln['label'],
        shape="circle",
        size=0,
        color="rgba(0,0,0,0)",
        font={'size': 240, 'color': '#000000', 'strokeWidth': 0, 'align': 'center'},
        physics=False,
        fixed=True,
        hidden=False
    )
    net.add_edge(ln['id'], ln['nodes'][0], hidden=True)
    net.add_edge(ln['id'], ln['nodes'][1], hidden=True)

# Customize edges (make main edges visible and set properties)
for edge in net.edges:
    if not edge.get('hidden', False):
        edge['color'] = 'black'
        edge['width'] = 30
        edge['label'] = edge.get('label', '')
        edge['font'] = {'size': 240, 'align': 'center'}
    else:
        edge['hidden'] = True

# Set Pyvis options to enable dragging and zooming without additional controls
net.set_options("""
{
  "nodes": {
    "shapeProperties": {
      "useBorderWithImage": false
    }
  },
  "edges": {
    "smooth": false
  },
  "physics": {
    "enabled": false
  },
  "interaction": {
    "dragNodes": true,
    "hover": true,
    "navigationButtons": false,
    "zoomView": true,
    "dragView": true
  },
  "layout": {
    "randomSeed": 42
  }
}
""")

# JavaScript code to dynamically position label nodes to avoid overlapping with links
js_code = """
function moveOpticalNodes() {
    var nodesDataset = network.body.data.nodes;

    function getMidpoint(pos1, pos2) {
        return {
            x: (pos1.x + pos2.x) / 2,
            y: (pos1.y + pos2.y) / 2
        };
    }

    // Update positions of optical nodes
    var opticalNodes = ['Optical Link 1', 'Optical Link 2', 'Optical Link 3'];
    opticalNodes.forEach(function(opticalNodeId) {
        var connectedNodes = network.getConnectedNodes(opticalNodeId);
        if (connectedNodes.length === 2) {
            var pos1 = network.getPosition(connectedNodes[0]);
            var pos2 = network.getPosition(connectedNodes[1]);
            var midpoint = getMidpoint(pos1, pos2);
            nodesDataset.update({
                id: opticalNodeId,
                x: midpoint.x,
                y: midpoint.y,
                hidden: false
            });
        }
    });
}

function moveLabelNodes() {
    var nodesDataset = network.body.data.nodes;

    function getQuarterPoint(pos1, pos2) {
        return {
            x: pos1.x + (pos2.x - pos1.x) * 0.25,
            y: pos1.y + (pos2.y - pos1.y) * 0.25
        };
    }

    function getPerpendicularOffset(pos1, pos2, offset) {
        var dx = pos2.x - pos1.x;
        var dy = pos2.y - pos1.y;
        var length = Math.sqrt(dx * dx + dy * dy);
        if (length === 0) return {x: 0, y: 0};
        var nx = dx / length;
        var ny = dy / length;
        var px = -ny;
        var py = nx;
        return {
            x: px * offset,
            y: py * offset
        };
    }

    // Define the offset distance for labels
    var labelOffset = 500; // Adjust this value as needed

    // Update positions of label nodes at 1/4 link length
    var labelNodes = ['Label Node 1', 'Label Node 2', 'Label Node 3'];
    labelNodes.forEach(function(labelNodeId) {
        var connectedNodes = network.getConnectedNodes(labelNodeId);
        if (connectedNodes.length === 2) {
            var pos1 = network.getPosition(connectedNodes[0]);
            var pos2 = network.getPosition(connectedNodes[1]);
            var quarterPos = getQuarterPoint(pos1, pos2);
            var offsetVector = getPerpendicularOffset(pos1, pos2, labelOffset);
            var newX = quarterPos.x + offsetVector.x;
            var newY = quarterPos.y + offsetVector.y;
            nodesDataset.update({
                id: labelNodeId,
                x: newX,
                y: newY
            });
        }
    });
}

// Initial positioning
moveOpticalNodes();
moveLabelNodes();

// Update positions after dragging nodes
network.on('dragEnd', function() {
    moveOpticalNodes();
    moveLabelNodes();
});
"""

# Generate and save the HTML
output_file = 'network_graph_with_images.html'
net.save_graph(output_file)

# Read the generated HTML content
with open(output_file, 'r', encoding='utf-8') as file:
    html_content = file.read()

# Insert the JavaScript code before the closing </body> tag
html_content = html_content.replace('</body>', f'<script type="text/javascript">{js_code}</script></body>')

# Write the modified HTML content back to the file
with open(output_file, 'w', encoding='utf-8') as file:
    file.write(html_content)

print(f"Network graph has been successfully generated and saved as '{output_file}'.")