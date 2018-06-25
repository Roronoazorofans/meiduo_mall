from django.db import models

"""创建行政区划模型类"""
class Area(models.Model):
    name = models.CharField(max_length=20, verbose_name="名称")
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='subs', null=True, blank=True, verbose_name='上级行政区划')

    class Meta:
        db_table = 'tb_areas'
        verbose_name = '行政区划'
        verbose_name_plural = '行政区划'

    def __str__(self):
        return self.name