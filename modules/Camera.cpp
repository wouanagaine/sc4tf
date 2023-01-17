#include "Camera.h"
#include "FrontEnd.h"

namespace GraphicEngine
{
// =============================================================================
// Camera
// =============================================================================

	Camera::Camera()
		: vPos_( 0, 0, -10 )
		, vAt_( 0, 0, 0 )
	{
	}
	Camera::~Camera()
	{
	}


	const D3DXVECTOR3& Camera::GetPos() const
	{
		return vPos_;
	}
	void Camera::SetPos( const D3DXVECTOR3& vPos )
	{
		vPos_ = vPos;
	}

	const D3DXVECTOR3& Camera::GetAt() const
	{
		return vAt_;
	}
	void Camera::SetAt( const D3DXVECTOR3& vAt )
	{
		vAt_ = vAt;
	}

// =============================================================================
// CameraRepresentation
// =============================================================================

	void Camera::Render( )
	{
		D3DXVECTOR3 vUp( 0, 1, 0 );
		D3DXMATRIX matView;
		D3DXMatrixLookAtRH( &matView,&vPos_,&vAt_, &vUp );
		GraphicEngine::FrontEnd::Ref().SetViewTransform( matView );
		D3DXMATRIXA16 matProj;
		D3DXMatrixPerspectiveFovRH( &matProj, D3DX_PI/4, 1.0f, 12.0f, 2048.0f*12 );
		//D3DXMatrixOrthoRH( &matProj, 256*12,256*12, 12.0f, 2048.0f*12 );
		D3DXMATRIX ViewProjMat;
		D3DXMatrixMultiply( &ViewProjMat, &matView, &matProj );

		frustrum_.ExtractFrustrum( ViewProjMat );
	}


	D3DXVECTOR3 Camera::RotateView( float rAngle, const D3DXVECTOR3& vAxis, D3DXVECTOR3& vAt, D3DXVECTOR3& vPos )
	{
		D3DXMATRIX mRot;
		D3DXMatrixRotationAxis( &mRot, &vAxis, rAngle );

		D3DXVECTOR3 vView = vAt - vPos;		
		D3DXVECTOR3 vNewView;
		D3DXVec3TransformCoord( &vNewView, &vView, &mRot );
		return vPos + vNewView;
	}

	void Camera::MoveUp( float amount )
	{
		D3DXVECTOR3 vUpVector( 0, 1, 0 );
		vPos_.y +=  vUpVector.y * amount;
		vAt_.y +=  vUpVector.y * amount;
	}

	void Camera::RotX( float amount )
	{
		D3DXVECTOR3 vStrafe;
		D3DXVECTOR3 vCross;
		D3DXVECTOR3 vUpVector( 0, 1, 0 );
		D3DXVECTOR3 vVector = vAt_ - vPos_;
		D3DXVec3Normalize( &vVector, &vVector );
		D3DXVec3Normalize( &vStrafe, D3DXVec3Cross( &vCross, &vVector, &vUpVector) );
		vAt_ = RotateView( amount, vStrafe, vAt_, vPos_ );
	}

	void Camera::RotY( float amount )
	{
		D3DXVECTOR3 vStrafe;
		D3DXVECTOR3 vCross;
		D3DXVECTOR3 vUpVector( 0, 1, 0 );
		D3DXVECTOR3 vVector = vAt_ - vPos_;
		D3DXVec3Normalize( &vVector, &vVector );
		D3DXVec3Normalize( &vStrafe, D3DXVec3Cross( &vCross, &vVector, &vUpVector) );
		vAt_ = RotateView( amount, vUpVector, vAt_, vPos_ );
	}

	void Camera::Strafe( float amount )
	{
		D3DXVECTOR3 vStrafe;
		D3DXVECTOR3 vCross;
		D3DXVECTOR3 vUpVector( 0, 1, 0 );
		D3DXVECTOR3 vVector = vAt_ - vPos_;
		D3DXVec3Normalize( &vVector, &vVector );
		D3DXVec3Normalize( &vStrafe, D3DXVec3Cross( &vCross, &vVector, &vUpVector) );

		vPos_.x +=  vStrafe.x * amount;
		vPos_.y +=  vStrafe.y * amount;
		vPos_.z +=  vStrafe.z * amount;
		vAt_.x +=  vStrafe.x * amount;
		vAt_.y +=  vStrafe.y * amount;
		vAt_.z +=  vStrafe.z * amount;
	}
	void Camera::Move( float amount )
	{
		D3DXVECTOR3 vStrafe;
		D3DXVECTOR3 vCross;
		D3DXVECTOR3 vUpVector( 0, 1, 0 );
		D3DXVECTOR3 vVector = vAt_ - vPos_;
		vVector.y = 0;
		D3DXVec3Normalize( &vVector, &vVector );
		D3DXVec3Normalize( &vStrafe, D3DXVec3Cross( &vCross, &vVector, &vUpVector) );

		vPos_.x +=  vVector.x * amount;
		vPos_.y +=  vVector.y * amount;
		vPos_.z +=  vVector.z * amount;
		vAt_.x +=  vVector.x * amount;
		vAt_.y +=  vVector.y * amount;
		vAt_.z +=  vVector.z * amount;
	}

}