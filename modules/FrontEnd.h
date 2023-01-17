#ifndef FrontEnd_included
#define FrontEnd_included

#include <string>
#include <dx/d3dx9.h>

struct IDirect3DDevice9;
struct D3DXMATRIX;


namespace GraphicEngine
{
	class TextureManager;
	class Texture;
	class ShaderManager;
	class FrontEnd
	{
		friend IDirect3DDevice9* GetDXDevice();
		friend class Shader;
		friend class FrontEndCreator;
		friend class TextureManager;
		ID3DXFont* pFont_;
		ID3DXSprite* pSprite_;
		TextureManager* pTexMgr_;
		ShaderManager* pShaderMgr_;
		IDirect3DDevice9* pD3DDevice_;

		D3DXMATRIX matWorld_;
		D3DXMATRIX matView_;
		D3DXMATRIX matInv_;
		D3DXMATRIX matProj_;
		int nbrFramesPerSecond_;
		int nbrFrames_;
		bool bDeviceLost_;
		static FrontEnd* pInstance_;

		explicit FrontEnd( IDirect3DDevice9* pDevice);
		~FrontEnd();
		FrontEnd();
		FrontEnd( const FrontEnd& rhs );

		void RenderText();
	public:
		static FrontEnd& Ref()
		{
			return *pInstance_;
		}
		static bool IsValid()
		{
			return pInstance_ != NULL;
		}

		Texture* GetTexture( const std::wstring& strTextureName );
		Shader* GetEffect( const std::wstring& strEffectName );
		void SetWorldTransform( const D3DXMATRIX& mat );
		void SetViewTransform( const D3DXMATRIX& mat );
		const D3DXMATRIX& GetViewTransform() const
		{
			return matView_;
		}

		const D3DXMATRIX& GetInvViewTransform() const;
		void SetProjTransform( const D3DXMATRIX& mat );
		void BeginScene();
		void EndScene();
		void Present();
		void Clear( unsigned long dwFlags, const unsigned long& color, float rZ, unsigned long dwStencil );
		void ComputeFPS();
		void WriteInfo( const std::wstring& strInfo );
		D3DXVECTOR3 Unproject( const D3DXVECTOR2& vScreen ) const;

	};

	class FrontEndCreator
	{
		FrontEnd* pFrontEnd_;
	public:
		FrontEndCreator( HWND hwnd, bool bWindowed );
		~FrontEndCreator();
	};

	inline
	IDirect3DDevice9* GetDXDevice()
	{
		return FrontEnd::Ref().pD3DDevice_;
	}

}
#endif