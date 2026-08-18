from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.shortcuts import get_object_or_404
from protest_app.models import Members
from protest_app.Serializers.MemberSerializer import MemberSerializer


class MemberAPI(APIView):
    def get(self, request, id=None):
        if id:
            member = get_object_or_404(Members, id=id)
            serializer = MemberSerializer(member)
            return Response({
                'status': True,
                'message': 'Member retrieved successfully.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        queryset = Members.objects.all().order_by('-id')

        is_deleted = request.query_params.get('is_deleted')
        if is_deleted is not None:
            queryset = queryset.filter(is_deleted=int(is_deleted))
        else:
            queryset = queryset.filter(is_deleted=0)

        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search) |
                Q(email__icontains=search) |
                Q(mobile_number__icontains=search) |
                Q(city__name__icontains=search) |
                Q(state__name__icontains=search) |
                Q(why_join__icontains=search)
            )

        state_id = request.query_params.get('state')
        city_id = request.query_params.get('city')
        if state_id:
            queryset = queryset.filter(state__id=state_id)
        if city_id:
            queryset = queryset.filter(city__id=city_id)

        all_records = request.query_params.get('all')
        serializer = MemberSerializer(queryset, many=True)
        return Response({
            'status': True,
            'message': 'Members listed successfully.',
            'count': queryset.count(),
            'results': serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = MemberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': True,
                'message': 'Member created successfully.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'status': False,
            'message': 'Invalid data.',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, id):
        member = get_object_or_404(Members, id=id)
        serializer = MemberSerializer(member, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': True,
                'message': 'Member updated successfully.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'status': False,
            'message': 'Invalid data.',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        member = get_object_or_404(Members, id=id)
        if member.is_deleted == 1:
            member.delete()
            return Response({
                'status': True,
                'message': 'Member permanently deleted.',
                'data': None
            }, status=status.HTTP_200_OK)
        member.is_deleted = 1
        member.save()
        return Response({
            'status': True,
            'message': 'Member moved to trash.',
            'data': None
        }, status=status.HTTP_200_OK)


class MemberRestoreAPI(APIView):
    def post(self, request, id):
        try:
            member = Members.objects.get(id=id)
        except Members.DoesNotExist:
            return Response({
                'status': False,
                'message': 'Member not found.',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)

        if member.is_deleted == 0:
            return Response({
                'status': False,
                'message': 'Member is not in trash.',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        member.is_deleted = 0
        member.save()
        serializer = MemberSerializer(member)
        return Response({
            'status': True,
            'message': 'Member restored successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
