from django.apps import AppConfig


class FaissManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'faiss_manager'
    verbose_name = 'FAISS Manager'

    def ready(self):
        """
        Initialize FAISS service when Django starts.
        This ensures the embedding model and FAISS indexes are loaded once.
        """
        # TODO: Uncomment when FAISSService is implemented
        # from faiss_manager.services import FAISSService
        # try:
        #     FAISSService.initialize()
        # except Exception as e:
        #     print(f"Could not initialize FAISS on startup: {e}")
        pass
