"""Read-only project checks; no editor or asset changes."""
import json
from pathlib import Path
from weaver_serialization import object_reference


def inspect_project(project_path, reports):
    project = Path(project_path)
    data = json.loads(project.read_text(encoding='utf-8-sig'))
    missing, external = set(), set()
    def visit(value):
        if isinstance(value, dict):
            if value.get('ObjectName') and value.get('ObjectPath'):
                try:
                    reference = object_reference(value)
                    path = reference.split("'", 1)[1].rstrip("'").split('.')[0]
                    if path.startswith('/Game/'):
                        asset = project.parent / 'Content' / (path[6:] + '.uasset')
                        if not asset.is_file():
                            missing.add(path)
                    else:
                        external.add(path)
                except ValueError:
                    external.add(str(value['ObjectPath']))
            for item in value.values():
                visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)
    for report in reports:
        for detail in report['classes'].values():
            for node in detail['nodes']:
                visit(node['data'])
    return {
        'project': str(project), 'engine': data.get('EngineAssociation', ''),
        'enabled_plugins': [p['Name'] for p in data.get('Plugins', []) if p.get('Enabled')],
        'missing_game_assets': sorted(missing), 'external_references_to_check': sorted(external),
        'note': 'Comprobación de rutas y configuración. No confirma carga de plugins, pegado ni compilación de nodos.',
    }
