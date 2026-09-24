"""Launch the Flask project catalogue and local model chat."""

from project_launcher import create_app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=False)
