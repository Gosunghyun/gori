from django.contrib.auth import get_user_model
from django.utils.datastructures import MultiValueDictKeyError
from rest_auth.registration.views import RegisterView
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from member.models import Tutor
from member.serializers import TutorSerializer
from member.serializers import UserSerializer
from member.serializers.login import CustomRegisterSerializer
from member.serializers.user import TutorInfoSerializer
from talent.models import WishList, Talent, Registration
from talent.serializers import TalentShortInfoSerializer, \
    MyRegistrationSerializer, MyPageWrapperSerializer, \
    MyApplicantsSerializer
from utils import verify_instance, LargeResultsSetPagination
from utils.remove_all_but_numbers import remove_non_numeric

__all__ = (
    'UserProfileView',
    'TutorProfileView',
    'TutorUpdateView',
    'UserRetrieveUpdateDestroyView',
    'CreateDjangoUserView',
    'MyWishListView',
    'MyRegistrationView',
    'MyEnrolledTalentView',
    'MyTalentsView',
    'MyApplicantsView',
    'WishListToggleView',
    'RegisterTutorView',
    'StaffUserVerifyTutorView',
    'StaffUserVerifyTalentView',
    'TutorVerifyRegistrationView',
    'MyPageView',
)

User = get_user_model()


# ##### 일반 유저 관련 #####
class UserProfileView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        user = request.user
        try:
            for request_item in request.data.keys():
                if request_item not in [item for item in UserSerializer(user).fields]:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "잘못된 형식의 data 입니다."})
            cellphone = request.data.get("cellphone", False)
            if cellphone and len(request.data["cellphone"]) == len(remove_non_numeric(cellphone)):
                serializer = UserSerializer(user, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(status=status.HTTP_200_OK, data=UserSerializer(user).data)
            elif cellphone and len(request.data["cellphone"]) != len(remove_non_numeric(cellphone)):
                return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "cellphone 에는 숫자만 입력해주세요."})
            else:
                serializer = UserSerializer(user, data=request.data, partial=True)
                if serializer.is_valid():
                    user.save()
                    serializer.save()
                    return Response(status=status.HTTP_200_OK, data=UserSerializer(user).data)
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "잘못된 형식의 data 입니다."})
        except MultiValueDictKeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "잘못된 형식의 data 입니다."})

    def delete(self, request, format=None):
        """
        유저 삭제할 때
        연결된 tutor, talent, review, qna 모두 삭제.
        """
        user = request.user
        user.delete()
        ret = {
            "detail": "유저가 삭제되었습니다."
        }
        return Response(ret)


class StaffUserVerifyTalentView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, talent_pk):
        user = request.user
        try:
            if user.is_staff:
                talent, detail = verify_instance(Talent, talent_pk)
                return Response(status=status.HTTP_200_OK,
                                data={"detail": detail, "result": TalentShortInfoSerializer(talent).data})
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED, data={"detail": "해당 요청에 대한 권한이 없습니다."})
        except Talent.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "해당 수업을 찾을 수 없습니다."})


class StaffUserVerifyTutorView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, tutor_pk):
        user = request.user
        try:
            if user.is_staff:
                tutor, detail = verify_instance(Tutor, tutor_pk)
                return Response(status=status.HTTP_200_OK,
                                data={"detail": detail})
                # data={"detail": detail, "result": TutorSerializer(tutor).data})
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED, data={"detail": "해당 요청에 대한 권한이 없습니다."})
        except Tutor.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "해당 튜터를 찾을 수 없습니다."})


class TutorVerifyRegistrationView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, registration_pk):
        user = request.user
        if hasattr(request.user, 'tutor'):
            try:
                registration = Registration.objects.get(pk=registration_pk)
                if registration.talent_location.talent in user.tutor.talent_set.all():
                    registration, detail = verify_instance(Registration, registration_pk)
                    return Response(status=status.HTTP_200_OK,
                                    data={"detail": detail})
                    # data={"detail": detail, "result": TalentRegistrationSerializer(registration).data})
                else:
                    return Response(status=status.HTTP_401_UNAUTHORIZED, data={"detail": "해당 요청에 대한 권한이 없습니다."})
            except Registration.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "해당 신청 내역을 찾을 수 없습니다."})
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={"detail": "해당 요청에 대한 권한이 없습니다."})


class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer


# ##### 튜터 관련 #####
class TutorProfileView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = TutorSerializer(Tutor.objects.get(user_id=user.id))
        return Response(serializer.data)


class TutorUpdateView(UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def patch(self, request, *args, **kwargs):
        user = request.user
        if hasattr(user, 'tutor'):
            try:
                tutor = user.tutor
                for request_item in request.data.keys():
                    if request_item not in [item for item in TutorInfoSerializer(tutor).fields]:
                        return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "잘못된 형식의 data 입니다."})
                    verification_method = request.data.get('verification_method', tutor.verification_method)
                    current_status = request.data.get('current_status', tutor.current_status)
                    if verification_method == 'UN' or 'GR':
                        if current_status == '':
                            return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "재학/졸업/수료 여부를 입력해주세요"})
                        serializer = TutorInfoSerializer(tutor, data=request.data, partial=True)
                        if serializer.is_valid():
                            serializer.save()
                            return Response(status=status.HTTP_200_OK, data={"detail": "튜터 정보가 수정되었습니다"})
                    else:
                        serializer = TutorSerializer(tutor, data=request.data, partial=True)
                        if serializer.is_valid():
                            serializer.save()
                            return Response(status=status.HTTP_200_OK, data={"detail": "튜터 정보가 수정되었습니다"})
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "잘못된 형식의 data 입니다"})
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'detail': "튜터로 등록되어 있지 않습니다"})


class CreateDjangoUserView(RegisterView):
    serializer_class = CustomRegisterSerializer


class RegisterTutorView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        """
        튜터 신청.
        1. 요청한 유저가 이미 튜터인지 확인한다.
        2. request 정보를 넘겨받아 튜터를 생성한다.

        필수정보 :
            - verification_method : 인증 수단
        추가정보 :
            - verification_images : 인증 이미지
            - school : 학교
            - major : 전공
            - current_status : 재학상태
        """
        user = request.user

        # 이미 튜터로 등록되어있는지
        tutor_list = Tutor.objects.values_list('user_id', flat=True)
        if user.id in tutor_list:
            ret = {
                'detail': '이미 튜터로 등록되어있습니다.'
            }
            return Response(ret, status=status.HTTP_400_BAD_REQUEST)

        try:
            verification_method = request.data['verification_method']
            verification_images = request.FILES['verification_images']
            school = request.data.get('school', '')
            major = request.data.get('major', '')
            current_status = request.data.get('current_status', '')

            Tutor.objects.create(
                user=user,
                verification_method=verification_method,
                verification_images=verification_images,
                school=school,
                major=major,
                current_status=current_status,
            )
            ret = {
                'detail': '튜터 신청이 완료되었습니다.'
            }
            return Response(ret, status=status.HTTP_201_CREATED)

        except MultiValueDictKeyError as e:
            ret = {
                'non_field_error': (str(e)).strip('"') + ' field가 제공되지 않았습니다.'
            }
            return Response(ret, status=status.HTTP_400_BAD_REQUEST)


class MyWishListView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TalentShortInfoSerializer
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        talents = Talent.objects.filter(wishlist_user=user)
        return talents.all()


# ##### 유저가 wishlist에 담기/빼기 #####
class WishListToggleView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk):
        user = User.objects.get(id=request.user.id)
        try:
            talent = Talent.objects.get(pk=pk)
            if talent.tutor.user != user:
                if talent.pk in user.my_wishlist.values_list('talent', flat=True):
                    wishlist = WishList.objects.filter(user=user, talent=talent)
                    wishlist.delete()
                    return Response(status=status.HTTP_200_OK,
                                    data={'detail': '수업 [{}]이(가) wishlist에서 삭제되었습니다.'.format(talent.title)})
                else:
                    WishList.objects.create(user=user, talent=talent)
                    return Response(status=status.HTTP_201_CREATED,
                                    data={'detail': '수업 [{}]이(가) wishlist에 추가되었습니다.'.format(talent.title)})
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'detail': '본인의 수업을 위시리스트에 담을 수 없습니다.'})
        except Talent.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'detail': '해당 수업을 찾을 수 없습니다.'})


# class MyRegistrationView(APIView):
#     permission_classes = (permissions.IsAuthenticated,)
#
#     def get(self, request):
#         user = User.objects.get(id=request.user.id)
#         serializer = MyRegistrationWrapperSerializer(user)
#         return Response(serializer.data)

class MyRegistrationView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = MyRegistrationSerializer
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        registrations = Registration.objects.filter(student=user).filter(is_verified=False)
        return registrations.all()


class MyEnrolledTalentView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = MyRegistrationSerializer
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        registrations = Registration.objects.filter(student=user).filter(is_verified=True)
        return registrations.all()


class MyTalentsView(generics.ListAPIView):
    serializer_class = TalentShortInfoSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        talents = Talent.objects.filter(tutor__user=self.request.user)
        return talents.all()


class MyApplicantsView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = MyApplicantsSerializer
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        registrations = []
        for talent in user.tutor.talent_set.all():
            registrations.extend([item for item in Registration.objects.filter(talent_location__talent=talent)])
        return registrations


class MyPageView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = User.objects.get(id=request.user.id)
        serializer = MyPageWrapperSerializer(user)
        return Response(serializer.data)
