from django.core.management.base import BaseCommand, CommandError
from pods.models import Pod
from core.utils import encode_video

class Command(BaseCommand):
	args = '<pod_id pod_id ...>'
	help = 'Encod the specified video'
	
	def handle(self, *args, **options):
		for pod_id in args:
			try:
				pod = Pod.objects.get(pk=int(pod_id))
			except Pod.DoesNotExist:
				raise CommandError('Pod "%s" does not exist' % pod_id)

			encode_video(pod)

			self.stdout.write('Successfully encode video "%s"' % pod_id)
