"""
Pointr CMS REST API

Manages Site -> Building -> Level resources.
Uses in-memory dictionaries for storage.
"""

from flask import Flask, jsonify, request
import uuid

app = Flask(__name__)

# In-memory data stores
sites = {}      # site_id -> {id, name, description}
buildings = {}  # building_id -> {id, name, site_id, floors}
levels = {}     # level_id -> {id, name, building_id, floor_number}


# ---------- Site API ----------

@app.route('/api/sites', methods=['POST'])
def create_site():
    # silent=True returns None instead of raising 415 when the request
    # has no/unsupported Content-Type or an empty body. This lets us
    # respond with a more helpful 400 validation error.
    data = request.get_json(silent=True)

    if not data or 'name' not in data:
        return jsonify({'error': 'name field is required'}), 400

    site_id = str(uuid.uuid4())
    sites[site_id] = {
        'id': site_id,
        'name': data['name'],
        'description': data.get('description', '')
    }

    return jsonify(sites[site_id]), 201


@app.route('/api/sites/<site_id>', methods=['GET'])
def get_site(site_id):
    site = sites.get(site_id)
    if not site:
        return jsonify({'error': 'Site not found'}), 404
    return jsonify(site), 200


@app.route('/api/sites/<site_id>', methods=['DELETE'])
def delete_site(site_id):
    if site_id not in sites:
        return jsonify({'error': 'Site not found'}), 404

    del sites[site_id]
    return jsonify({'message': 'Site successfully deleted'}), 200


# ---------- Building API ----------

@app.route('/api/buildings', methods=['POST'])
def create_building():
    data = request.get_json(silent=True)

    if not data or 'name' not in data or 'site_id' not in data:
        return jsonify({'error': 'name and site_id fields are required'}), 400

    if data['site_id'] not in sites:
        return jsonify({'error': 'Specified site_id not found'}), 404

    building_id = str(uuid.uuid4())
    buildings[building_id] = {
        'id': building_id,
        'name': data['name'],
        'site_id': data['site_id'],
        'floors': data.get('floors', 1)
    }

    return jsonify(buildings[building_id]), 201


@app.route('/api/buildings/<building_id>', methods=['GET'])
def get_building(building_id):
    building = buildings.get(building_id)
    if not building:
        return jsonify({'error': 'Building not found'}), 404
    return jsonify(building), 200


@app.route('/api/buildings/<building_id>', methods=['DELETE'])
def delete_building(building_id):
    if building_id not in buildings:
        return jsonify({'error': 'Building not found'}), 404

    del buildings[building_id]
    return jsonify({'message': 'Building successfully deleted'}), 200


# ---------- Level API ----------

@app.route('/api/levels', methods=['POST'])
def import_levels():
    """
    Import a single level (object) or multiple levels (list).
    Returns 201 with both 'created' and 'errors' lists so partial
    imports don't lose valid entries.
    """
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({'error': 'Invalid or missing JSON body'}), 400

    level_list = data if isinstance(data, list) else [data]

    created = []
    errors = []

    for level_data in level_list:
        if not level_data.get('name') or not level_data.get('building_id'):
            errors.append({
                'error': 'name and building_id are required',
                'data': level_data
            })
            continue

        if level_data['building_id'] not in buildings:
            errors.append({
                'error': 'building_id not found',
                'data': level_data
            })
            continue

        level_id = str(uuid.uuid4())
        levels[level_id] = {
            'id': level_id,
            'name': level_data['name'],
            'building_id': level_data['building_id'],
            'floor_number': level_data.get('floor_number', 0)
        }
        created.append(levels[level_id])

    return jsonify({'created': created, 'errors': errors}), 201


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
