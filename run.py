# -*- coding: utf-8 -*-
import os
from app import create_app, db
from app.models import User, Role, ElderlyProfile, VolunteerProfile, WorkerProfile, CommunityAdminProfile

app = create_app(os.getenv('FLASK_ENV') or 'default')


@app.shell_context_processor
def make_shell_context():
    return dict(
        db=db,
        User=User,
        Role=Role,
        ElderlyProfile=ElderlyProfile,
        VolunteerProfile=VolunteerProfile,
        WorkerProfile=WorkerProfile,
        CommunityAdminProfile=CommunityAdminProfile
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
