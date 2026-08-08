from rest_framework import status
from rest_framework.views import APIView, Response
from .serializers import ParentSerializer, LSAProfileSerializer
from .models import LSAProfile
from rest_framework.permissions import AllowAny

class ParentView(APIView):

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = ParentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({
                    "message": "Parent Profile created successfully!",
                    "data": serializer.data,
                    },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )



class LSASearchView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):
        skill = request.query_params.get("skill")
        queryset = LSAProfile.objects.filter(is_active=True)

        if skill:
            queryset = queryset.filter(
                skills__icontains=skill
            )

        count = queryset.count()

        serializer = LSAProfileSerializer(
            queryset,
            many=True
        )

        return Response({
            "message": f"Found {count} LSAs!",
            "data": serializer.data,
        },status=status.HTTP_200_OK)

