from rest_framework import serializers
from users.models import Employee
from plans.models import Task


class EmployeeSerializer(serializers.ModelSerializer):
    idp_status = serializers.SerializerMethodField()
    mentor_id = serializers.SerializerMethodField()
    idp_id = serializers.SerializerMethodField()
    last_name = serializers.ReadOnlyField(source='user.last_name')
    first_name = serializers.ReadOnlyField(source='user.first_name')
    middle_name = serializers.ReadOnlyField(source='user.middle_name')
    message = serializers.SerializerMethodField()
    task_count = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ['id',
                  'head',
                  'mentor_id',
                  'idp_id',
                  'last_name',
                  'first_name',
                  'middle_name',
                  'grade',
                  'position',
                  'task_count',
                  'idp_status',
                  'message',
                  ]

    def get_idp_status(self, obj):
        idps = obj.IDP.all()
        if idps.exists():
            return idps.first().execution_status.name
        else:
            return None

    def get_mentor_id(self, obj):
        return obj.mentor.exists()

    def get_idp_id(self, obj):
        idps = obj.IDP.all()
        if idps.exists():
            return idps.first().id
        else:
            return None

    def get_message(self, obj):
        idps = obj.IDP.all()
        if idps.exists():
            return idps.first().message
        else:
            return None

    def get_task_count(self, obj):
        tasks = Task.objects.filter(idp__employee=obj)
        return tasks.count()

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     representation['head_id'] = representation.pop('head')
    #     representation['employee_id'] = representation.pop('id')
    #     return representation
