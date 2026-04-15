from rest_framework import serializers
from .models import User

# serializer pentru creare user
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
     # transforma json in obiect user pentru a putea fi folosit in autentificare