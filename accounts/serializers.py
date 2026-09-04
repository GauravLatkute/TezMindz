from rest_framework import serializers
from django.contrib.auth.models import User
from accounts.models import StudentProfile
from academics.models import Class

class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ["id", "grade_number", "name", "class_label", "stage", "age_group", "category"]


class StudentProfileSerializer(serializers.ModelSerializer):
    student_class = ClassSerializer(read_only=True)
    class_id = serializers.PrimaryKeyRelatedField(
        queryset=Class.objects.all(),
        source="student_class",
        write_only=True
    )

    class Meta:
        model = StudentProfile
        fields = [
            "avatar",
            "dob",
            "xp",
            "coins",
            "current_level",
            "streak",
            "student_class",
            "class_id",
            "last_activity_date",
            "is_premium",
        ]
        read_only_fields = ["xp", "coins", "current_level", "streak", "last_activity_date", "is_premium"]


class UserSerializer(serializers.ModelSerializer):
    profile = StudentProfileSerializer()

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "profile"]

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", {})
        
        # Update User fields
        instance.email = validated_data.get("email", instance.email)
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.save()

        # Update Profile fields
        profile = instance.profile
        profile.avatar = profile_data.get("avatar", profile.avatar)
        profile.dob = profile_data.get("dob", profile.dob)
        if "student_class" in profile_data:
            profile.student_class = profile_data["student_class"]
        profile.save()

        return instance


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=6)
    class_id = serializers.PrimaryKeyRelatedField(
        queryset=Class.objects.all(),
        write_only=True
    )
    avatar = serializers.CharField(required=False, default="🌟")

    class Meta:
        model = User
        fields = ["username", "email", "password", "class_id", "avatar"]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        username = validated_data["username"]
        email = validated_data["email"]
        password = validated_data["password"]
        class_obj = validated_data["class_id"]
        avatar = validated_data.get("avatar", "🌟")

        # Create Django User
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Create Profile
        StudentProfile.objects.create(
            user=user,
            student_class=class_obj,
            avatar=avatar
        )

        return user
