from member.models import Tutor
from talent.models import Talent


def tutor_verify(request, model):
    """
    1. 요청하는 유저가 튜터인지 확인을 먼저 한 후
    2. 추가하고자 하는 talent의 튜터와 요청하는 유저(튜터)의 정보가 같은지 확인한다.
    """
    tutor_list = Tutor.objects.values_list('user_id', flat=True)
    user = request.user
    if user.id in tutor_list:
        if model.tutor == user.tutor:
            return True
    return False


def duplicate_verify(model, data):
    """
    특정 모델을 넘겨 받아 해당 data으로 구성된 아이템이 존재하는지 체크
    :param model: 중복체크하고자 하는 모델
    :param data:
    :return:
    """
    ret = {
        'detail': '이미 존재하는 항목입니다.'
    }
    if model.objects.filter(**data).count() > 0:
        return True, ret
    else:
        return False, {}


def verify_instance(model, pk):
    instance = model.objects.get(pk=pk)
    if instance.is_verified:
        instance.is_verified = False
        detail = "인증 취소되었습니다."
    else:
        instance.is_verified = True
        detail = "인증 되었습니다."
    instance.save()
    return instance, detail

def switch_sales_status(pk):
    talent = Talent.objects.get(pk=pk)
    if talent.is_soldout:
        talent.is_soldout = False
        detail = "SOLD OUT 취소되었습니다."
    else:
        talent.is_soldout = True
        detail = "SOLD OUT 되었습니다."
    talent.save()
    return talent, detail