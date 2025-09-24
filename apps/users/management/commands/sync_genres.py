from django.core.management.base import BaseCommand
from apps.movies.services import TMDbService


class Command(BaseCommand):
    help = 'Sync movie genres from TMDb API to local database'

    def handle(self, *args, **options):
        tmdb_service = TMDbService()
        
        self.stdout.write('Syncing genres from TMDb...')
        
        try:
            tmdb_service.sync_genres()
            self.stdout.write(
                self.style.SUCCESS('Successfully synced genres from TMDb')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to sync genres: {str(e)}')
            )