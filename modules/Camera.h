#ifndef Camera_included
#define Camera_included

#include <dx/d3Dx9.h>
#include "frustrum.h"
namespace GraphicEngine
{

	class Camera
	{
		D3DXVECTOR3 vPos_;
		D3DXVECTOR3 vAt_;
		Frustrum frustrum_;
	public:
		Camera();
		~Camera();

		void Render();

		const D3DXVECTOR3& GetPos() const;
		void SetPos( const D3DXVECTOR3& vPos );

		const D3DXVECTOR3& GetAt() const;
		void SetAt( const D3DXVECTOR3& vAt );

		Frustrum& GetFrustrum()
		{
			return frustrum_;
		}
		void Strafe( float amount);
		void Move( float amount );
		D3DXVECTOR3 RotateView( float rAngle, const D3DXVECTOR3& vAxis, D3DXVECTOR3& vAt, D3DXVECTOR3& vPos );
		void RotX( float amount );
		void RotY( float amount );
		void MoveUp( float amount );
	};

}

#endif