from backend.app import create_app

def test_routes():
    """Manually force route registration for debugging."""
    app = create_app()
    
    # ✅ Check if blueprints are already registered
    print("Registered Blueprints:", app.blueprints.keys())

    if "webhook" not in app.blueprints:
        from backend.routes import register_blueprints
        register_blueprints(app)  # Register only if not already registered

    with app.app_context():
        print("=== Available Routes in Test ===")
        for rule in app.url_map.iter_rules():
            print(rule)
        print("===============================")
