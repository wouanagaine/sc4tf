#ifndef Frustrum_included
#define Frustrum_included

#include <dx\d3dx9.h>
#include "Culling.h"

namespace GraphicEngine
{
	
struct BBox
{
	float vMin_[3];
	float vMax_[3];

	BBox( const BBox& rhs )
	{
		for( int i = 0; i<3;++i )
		{
			vMin_[i] = rhs.vMin_[i];
			vMax_[i] = rhs.vMax_[i];
		}
	}
	BBox()
	{
		vMin_[0] = 1000000;
		vMin_[1] = 1000000;
		vMin_[2] = 1000000;

		vMax_[0] = -1000000;
		vMax_[1] = -1000000;
		vMax_[1] = -1000000;
	}
	void ExpandBy( float* v )
	{
		for( int i = 0; i<3; ++i )
		{
			vMin_[i] = v[i]<vMin_[i]?v[i]:vMin_[i];
			vMax_[i] = v[i]>vMax_[i]?v[i]:vMax_[i];
		}
	}

	void ExpandBy( D3DXVECTOR3 vx )
	{
		float v[3] = { vx.x,vx.y,vx.z };
		ExpandBy( v );
	}
	void ExpandBy( float x, float y, float z )
	{
		float v[3] = { x,y,z };
		ExpandBy( v );
	}
	D3DXVECTOR3 GetMin() const
	{
		return D3DXVECTOR3( vMin_[0],vMin_[1],vMin_[2]);
	}
	D3DXVECTOR3 GetMax() const
	{
		return D3DXVECTOR3( vMax_[0],vMax_[1],vMax_[2]);
	}
/*
	bool IsVisible()
	{
		typedef float Vec[3];
		Vec vPoints[8] =
		{
			{ vMin_[0], vMin_[1], vMin_[2] },
			{ vMin_[0], vMin_[1], vMax_[2] },
			{ vMin_[0], vMax_[1], vMin_[2]},
			{ vMin_[0], vMax_[1], vMax_[2]},
			{ vMax_[0], vMin_[1], vMin_[2]},
			{ vMax_[0], vMin_[1], vMax_[2]},
			{ vMax_[0], vMax_[1], vMin_[2]},
			{ vMax_[0], vMax_[1], vMax_[2]}
		};

		unsigned int iCount2 = 0;
		for( unsigned int iCurPlane = 0; iCurPlane < 6; ++iCurPlane )
		{
			unsigned int iCount1 = 0;
			for( unsigned int iCurPoint = 0; iCurPoint < 8; ++iCurPoint )
			{
				if( frustum[ iCurPlane ].Distance( vPoints[ iCurPoint ] ) > 0 )
					++iCount1;
			}
			if( iCount1 == 0 )
				return false;
			if( iCount1 == 8 )
				++iCount2;
		}
		return true;
	}
	*/
};


	class Frustrum
	{
		enum E_PlaneSide
		{
			ePlaneRight = 0,
			ePlaneLeft,
			ePlaneBottom,
			ePlaneTop,
			ePlaneFar,
			ePlaneNear
		};		

		D3DXPLANE planes_[6];

	public:
		Frustrum();
		~Frustrum();

		void ExtractFrustrum( const D3DMATRIX& mat );

		Culling::E_CullingLocation CullBBox( const BBox& bbox ) const;
		Culling::E_CullingLocation CullBBox( const D3DXVECTOR3& vMin, const D3DXVECTOR3& vMax ) const;
		

	};
};
#endif
