#include "Frustrum.h"

namespace GraphicEngine
{


Frustrum::Frustrum()
{
}


Frustrum::~Frustrum()
{
}



void Frustrum::ExtractFrustrum( const D3DMATRIX& mat )
{
	D3DXPLANE plane;

	plane.a = mat._14 - mat._11;
	plane.b = mat._24 - mat._21;
	plane.c = mat._34 - mat._31;
	plane.d = mat._44 - mat._41;	
	D3DXPlaneNormalize( &planes_[ ePlaneRight ], &plane );

	plane.a = mat._14 + mat._11;
	plane.b = mat._24 + mat._21;
	plane.c = mat._34 + mat._31;
	plane.d = mat._44 + mat._41;	
	D3DXPlaneNormalize( &planes_[ ePlaneLeft ], &plane );

	plane.a = mat._14 + mat._12;
	plane.b = mat._24 + mat._22;
	plane.c = mat._34 + mat._32;
	plane.d = mat._44 + mat._42;	
	D3DXPlaneNormalize( &planes_[ ePlaneBottom ], &plane );

	plane.a = mat._14 - mat._12;
	plane.b = mat._24 - mat._22;
	plane.c = mat._34 - mat._32;
	plane.d = mat._44 - mat._42;	
	D3DXPlaneNormalize( &planes_[ ePlaneTop ], &plane );

	plane.a = mat._14 - mat._13;
	plane.b = mat._24 - mat._23;
	plane.c = mat._34 - mat._33;
	plane.d = mat._44 - mat._43;	
	D3DXPlaneNormalize( &planes_[ ePlaneFar ], &plane );

	plane.a = mat._14 + mat._13;
	plane.b = mat._24 + mat._23;
	plane.c = mat._34 + mat._33;
	plane.d = mat._44 + mat._43;	
	D3DXPlaneNormalize( &planes_[ ePlaneNear ], &plane );
}



Culling::E_CullingLocation Frustrum::CullBBox( const D3DXVECTOR3& vMin, const D3DXVECTOR3& vMax ) const
{
	D3DXVECTOR4 vPoints[8] =
	{
		D3DXVECTOR4( vMin.x, vMin.y, vMin.z, 1.f ),
		D3DXVECTOR4( vMin.x, vMin.y, vMax.z, 1.f ),
		D3DXVECTOR4( vMin.x, vMax.y, vMin.z, 1.f ),
		D3DXVECTOR4( vMin.x, vMax.y, vMax.z, 1.f ),
		D3DXVECTOR4( vMax.x, vMin.y, vMin.z, 1.f ),
		D3DXVECTOR4( vMax.x, vMin.y, vMax.z, 1.f ),
		D3DXVECTOR4( vMax.x, vMax.y, vMin.z, 1.f ),
		D3DXVECTOR4( vMax.x, vMax.y, vMax.z, 1.f )
	};


	unsigned int iCount2 = 0;
	for( unsigned int iCurPlane = 0; iCurPlane < 6; ++iCurPlane )
	{
		unsigned int iCount1 = 0;
		for( unsigned int iCurPoint = 0; iCurPoint < 8; ++iCurPoint )
		{
			if( D3DXPlaneDot( &planes_[ iCurPlane ], &vPoints[ iCurPoint ] ) > 0 )
				++iCount1;
		}
		if( iCount1 == 0 )
			return Culling::eCullingFullOutside;
		if( iCount1 == 8 )
			++iCount2;
	}
	return ( iCount2 == 6 ? Culling::eCullingFullInside : Culling::eCullingPartialInside );
}


Culling::E_CullingLocation Frustrum::CullBBox( const BBox& bbox ) const
{
	return CullBBox( bbox.GetMin(), bbox.GetMax() );
}

}