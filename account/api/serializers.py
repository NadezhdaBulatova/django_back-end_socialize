from rest_framework import serializers
from account.models import UserAccount, UserProfile
from rest_framework.validators import UniqueValidator
from django.core.exceptions import ValidationError


class UserAccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(required=True, validators = [UniqueValidator(queryset=UserAccount.objects.all())])
    username = serializers.CharField(required=True, validators = [UniqueValidator(queryset=UserAccount.objects.all())])
    class Meta:
        model = UserAccount
        fields = ['id', 'email', 'username', 'password']
    
    def create(self, validated_data):
        user = UserAccount.objects.create(email=validated_data['email'], username=validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=UserAccount.objects.all())
    friends = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all(), many=True, required=False)
    profile_img = serializers.ImageField(required=False)
    background_img = serializers.ImageField(required=False)

    class Meta:
        model = UserProfile
        fields = ['user', 'name', 'last_name', 'status', 'bio', 'profile_img', 'background_img','location', "friends", 'user']

    def validate(self, data):
        friends_pks = data.get('friends', [])
        friends = UserProfile.objects.filter(pk__in=friends_pks)
        if self.instance:
            friends = friends.exclude(pk=self.instance.pk)
        if self.instance and self.instance.pk in friends.values_list('pk', flat=True):
            raise ValidationError('A user cannot be friend with themselves.')
        return data
    
class UserProfileWithUserInfoSerializer(serializers.ModelSerializer):
    user = UserAccountSerializer()
    friends = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all(), many=True, required=False)
    profile_img = serializers.ImageField(required=False)
    background_img = serializers.ImageField(required=False)

    class Meta:
        model = UserProfile
        fields = ['user', 'name', 'last_name', 'status', 'bio', 'profile_img', 'background_img','location', "friends", 'user']

class UserProfileSimplifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user_id']
    