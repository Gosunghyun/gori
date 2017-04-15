from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response

from talent.models import Talent, Location
from talent.serializers import LocationSerializer, LocationCreateSerializer
from utils import *

__all__ = (
    'LocationListCreateView',
)


class LocationListCreateView(generics.ListCreateAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        return Location.objects.filter(talent_id=self.kwargs['pk'])

    def create(self, request, *args, **kwargs):
        # 생성 전용 시리얼라이저 사용
        serializer = LocationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # ##### 추가 검증 절차 #####
        talent = Talent.objects.get(pk=request.data['talent_pk'])

        # ##### 자신의 수업이면 등록 불가능 #####
        if verify_tutor(request, talent):
            return Response(talent_owner_error, status=status.HTTP_400_BAD_REQUEST)

        # ##### 이미 리뷰가 존재하면 등록 불가능#####
        data = {
            'talent': talent,
            'user': request.user,
        }
        if verify_duplicate(Review, data=data):
            return Response(multiple_item_error, status=status.HTTP_400_BAD_REQUEST)

        # ##### 추가 검증 끝  #####

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        # 성공 메시지 출력
        ret_message = '[{talent}]에 리뷰가 추가되었습니다.'.format(
            talent=talent.title,
        )
        ret = {
            'detail': ret_message,
        }
        return Response(ret, status=status.HTTP_201_CREATED, headers=headers)

    def post(self, request, *args, **kwargs):
        """

        필수정보 :
            - talent_pk : 수업 아이디
            - region : 지역에 대한 키 값
            - specific_location : 세부 지역에 대한 결정 여부
            - day : 요일
            - time : 시간
            - extra_fee : 추가 요금 있는지 여부
        추가정보 :
            - extra_fee_amount : 추가 요금 설명
            - location_info : 장소 세부 정보
        """
        try:
            talent_pk = request.data['talent_pk']
            region = request.data['region']
            specific_location = request.data['specific_location']
            day = request.data['day']
            time = request.data['time']
            extra_fee = request.data['extra_fee']

            talent = Talent.objects.filter(pk=talent_pk).first()
            if not talent:
                ret = {
                    'detail': '수업({pk})이 존재하지 않습니다.'.format(pk=talent_pk)
                }
                return Response(ret, status=status.HTTP_400_BAD_REQUEST)

            data = {
                'talent': talent,
                'region': region,
                'day': day
            }
            is_dup, msg = verify_duplicate(Location, data)
            if is_dup:
                return Response(msg, status=status.HTTP_400_BAD_REQUEST)

            if verify_tutor(request, talent):
                Location.objects.create(
                    talent=talent,
                    region=region,
                    specific_location=specific_location,
                    day=day,
                    time=time,
                    extra_fee=extra_fee,
                    # 필수정보가 아닌 경우 아래에 해당
                    extra_fee_amount=request.data.get('extra_fee_amount', ''),
                    location_info=request.data.get('location_info', ''),
                )

                ret_message = '[{talent}]에 [{region}] 지역이 추가되었습니다.'.format(
                    talent=talent.title,
                    region=region
                )
                ret = {
                    'detail': ret_message,
                }
                return Response(ret, status=status.HTTP_201_CREATED)

            ret = {
                'detail': '권한이 없습니다.',
            }
            return Response(ret, status=status.HTTP_401_UNAUTHORIZED)

        except MultiValueDictKeyError as e:
            ret = {
                'non_field_error': (str(e)).strip('"') + ' field가 제공되지 않았습니다.'
            }
            return Response(ret, status=status.HTTP_400_BAD_REQUEST)
