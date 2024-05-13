import click
import getpass
from app import app, db
from app.models import Admin


@app.cli.command('create-admin')
@click.argument('username')
def create_admin(username):
    try:
        existing_admin = Admin.query.filter_by(username=username).first()
        if existing_admin:
            click.echo('Admin already exists.')
        else:
            password = getpass.getpass('Enter password for the new admin (at least 8 characters): ')
            if len(password) < 8:
                click.echo('Password must be at least 8 characters long.')
                return
            confirm_password = getpass.getpass('Confirm password: ')
            if password != confirm_password:
                click.echo('Passwords do not match.')
                return
            new_admin = Admin(username=username)
            new_admin.set_password(password)
            db.session.add(new_admin)
            db.session.commit()
            click.echo('Admin created successfully.')
    except Exception as e:
        click.echo(f'Error: {str(e)}')
        db.session.rollback()


@app.cli.command('remove-admin')
@click.argument('username')
def remove_admin(username):
    try:
        admin_to_remove = Admin.query.filter_by(username=username).first()
        if admin_to_remove:
            confirmation = click.prompt('Are you sure you want to remove this admin? (yes/no)', type=str)
            if confirmation.lower() == 'yes':
                db.session.delete(admin_to_remove)
                db.session.commit()
                click.echo('Admin removed successfully.')
            else:
                click.echo('Removal canceled.')
        else:
            click.echo('Admin does not exist.')
    except Exception as e:
        click.echo(f'Error: {str(e)}')
        db.session.rollback()
