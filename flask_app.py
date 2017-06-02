from membership.web.members import app


# For running as script
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
