from rest_framework import serializers
from .models import Student, Major

class StudentSerializer(serializers.ModelSerializer):
    major = serializers.SlugRelatedField(
        slug_field='major',
        queryset=Major.objects.all()
    )

    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'email', 'banner_id', 'j_or_s', 'major', 'alternative_major']