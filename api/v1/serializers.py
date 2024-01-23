from rest_framework import serializers

from plans.models import IDP


class IDPSerializer(serializers.ModelSerializer):

    class Meta:
        model = IDP
        fields = ('id', 'author', 'employee', 'name', 'deadline', 'execution_status')
