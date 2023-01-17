#include "FrontEnd.h"
#include "TextureManager.h"
#include "Shader.h"
#include <dx/d3d9.h>
#include <dx/dxerr9.h>
#include "logger.h"

namespace Detail
{

	class TextHelper
	{
	public:
		TextHelper( ID3DXFont* pFont, ID3DXSprite* pSprite, int nLineHeight );

		void SetInsertionPos( int x, int y ) { m_pt.x = x; m_pt.y = y; }
		void SetForegroundColor( D3DXCOLOR clr ) { m_clr = clr; }

		void Begin();
		HRESULT DrawFormattedTextLine( const WCHAR* strMsg, ... );
		HRESULT DrawTextLine( const WCHAR* strMsg );
		HRESULT DrawFormattedTextLine( RECT &rc, DWORD dwFlags, const WCHAR* strMsg, ... );
		HRESULT DrawTextLine( RECT &rc, DWORD dwFlags, const WCHAR* strMsg );
		void End();

	protected:
		ID3DXFont*   m_pFont;
		ID3DXSprite* m_pSprite;
		D3DXCOLOR    m_clr;
		POINT        m_pt;
		int          m_nLineHeight;
	};
	//--------------------------------------------------------------------------------------
	TextHelper::TextHelper( ID3DXFont* pFont, ID3DXSprite* pSprite, int nLineHeight )
	{
		m_pFont = pFont;
		m_pSprite = pSprite;
		m_clr = D3DXCOLOR(1,1,1,1);
		m_pt.x = 0; 
		m_pt.y = 0; 
		m_nLineHeight = nLineHeight;
	}


	//--------------------------------------------------------------------------------------
	HRESULT TextHelper::DrawFormattedTextLine( const WCHAR* strMsg, ... )
	{
		WCHAR strBuffer[512];

		va_list args;
		va_start(args, strMsg);
		_vsnwprintf( strBuffer, 512, strMsg, args );
		strBuffer[511] = L'\0';
		va_end(args);

		return DrawTextLine( strBuffer );
	}


	//--------------------------------------------------------------------------------------
	HRESULT TextHelper::DrawTextLine( const WCHAR* strMsg )
	{
		if( NULL == m_pFont ) 
			return E_INVALIDARG;

		HRESULT hr;
		RECT rc;
		SetRect( &rc, m_pt.x, m_pt.y, 0, 0 ); 
		hr = m_pFont->DrawText( m_pSprite, strMsg, -1, &rc, DT_NOCLIP, m_clr );
		if( FAILED(hr) )
			return hr ;

		m_pt.y += m_nLineHeight;

		return S_OK;
	}


	HRESULT TextHelper::DrawFormattedTextLine( RECT &rc, DWORD dwFlags, const WCHAR* strMsg, ... )
	{
		WCHAR strBuffer[512];

		va_list args;
		va_start(args, strMsg);
		_vsnwprintf( strBuffer, 512, strMsg, args );
		strBuffer[511] = L'\0';
		va_end(args);

		return DrawTextLine( rc, dwFlags, strBuffer );
	}


	HRESULT TextHelper::DrawTextLine( RECT &rc, DWORD dwFlags, const WCHAR* strMsg )
	{
		if( NULL == m_pFont ) 
			return E_INVALIDARG;

		HRESULT hr;
		hr = m_pFont->DrawText( m_pSprite, strMsg, -1, &rc, dwFlags, m_clr );
		if( FAILED(hr) )
			return hr;

		m_pt.y += m_nLineHeight;

		return S_OK;
	}


	//--------------------------------------------------------------------------------------
	void TextHelper::Begin()
	{
		if( m_pSprite )
			m_pSprite->Begin( D3DXSPRITE_ALPHABLEND | D3DXSPRITE_SORT_TEXTURE );
	}
	void TextHelper::End()
	{
		if( m_pSprite )
			m_pSprite->End();
	}



	template< class T >
	struct ZeroedMemory
		: public T
	{
		ZeroedMemory()
		{
			ZeroMemory( this, sizeof( T ) );
		}
	};

}

namespace GraphicEngine
{

FrontEnd* FrontEnd::pInstance_ = 0;

FrontEndCreator::FrontEndCreator( HWND hwnd, bool bWindowed )
{
	IDirect3D9* pD3D = Direct3DCreate9( D3D_SDK_VERSION );
	if( !pD3D )
	{
	    printf( "Can't create DX9 ! \n" );
	}
	D3DPRESENT_PARAMETERS d3dpp;
	memset( &d3dpp, 0, sizeof( d3dpp ) );
	
	d3dpp.Windowed = bWindowed;
	d3dpp.SwapEffect = D3DSWAPEFFECT_FLIP;
	d3dpp.BackBufferFormat = D3DFMT_UNKNOWN;
	d3dpp.EnableAutoDepthStencil = TRUE;
	d3dpp.AutoDepthStencilFormat = D3DFMT_D24X8;
	d3dpp.BackBufferCount = 1;

	RECT rc;
	GetClientRect( hwnd, &rc);
	d3dpp.BackBufferWidth = rc.right-rc.left;
	d3dpp.BackBufferHeight = rc.bottom-rc.top;
	if( !bWindowed )
	{
		d3dpp.BackBufferFormat = D3DFMT_X8R8G8B8;
		d3dpp.BackBufferWidth = rc.right-rc.left;
		d3dpp.BackBufferHeight = rc.bottom-rc.top;
	}
	std::pair< int,D3DFORMAT > testers[] = {
		std::make_pair( D3DCREATE_HARDWARE_VERTEXPROCESSING, D3DFMT_D24X8 ),
		std::make_pair( D3DCREATE_HARDWARE_VERTEXPROCESSING, D3DFMT_D16 ),
		std::make_pair( D3DCREATE_MIXED_VERTEXPROCESSING, D3DFMT_D24X8 ),
		std::make_pair( D3DCREATE_MIXED_VERTEXPROCESSING, D3DFMT_D16 ),
		std::make_pair( D3DCREATE_SOFTWARE_VERTEXPROCESSING, D3DFMT_D24X8 ),
		std::make_pair( D3DCREATE_SOFTWARE_VERTEXPROCESSING, D3DFMT_D16 ),
	};
    std::wstring strs[] = 
    {
        L"HARDWARE VP WITH 24bit ZBuffer\n",
        L"HARDWARE VP WITH 16bit ZBuffer\n",
        L"MIXED VP WITH 24bit ZBuffer\n",
        L"MIXED VP WITH 16bit ZBuffer\n",
        L"SOFTWARE VP WITH 24bit ZBuffer\n",
        L"SOFTWARE VP WITH 16bit ZBuffer\n",        
    };
	for( int i = 0; i < 6; ++i)
	{
	IDirect3DDevice9* pD3DDevice = 0;
	d3dpp.AutoDepthStencilFormat = testers[i].second;
	HRESULT hr = pD3D->CreateDevice( D3DADAPTER_DEFAULT, D3DDEVTYPE_HAL, hwnd, testers[i].first, &d3dpp, &pD3DDevice);
	if( pD3DDevice )
	{
		pFrontEnd_ = new FrontEnd( pD3DDevice);
		Logger::Log( LOGGING, strs[i] );
		printf("Ok\n" );	
		return;
		break;
	}
	else
	{
		std::wstring str = DXGetErrorString9( hr );		
		Logger::Log( LOGGING, str+L"CreateDevice\n" );
	}
	Logger::Log( LOGGING, L"Can't create a valid DX9 Device\n" );
}



}

FrontEndCreator::~FrontEndCreator()
{
	delete pFrontEnd_;
	pFrontEnd_ = 0;
}


FrontEnd::FrontEnd( IDirect3DDevice9* pD3DDevice )
: pD3DDevice_( pD3DDevice )
, pTexMgr_( 0 )
, pShaderMgr_( 0 )
, pFont_( 0 )
, pSprite_( 0 )
, nbrFrames_( 0 )
, nbrFramesPerSecond_( 0 )
, bDeviceLost_( false )
{
	pInstance_ = this;
	pTexMgr_ = new TextureManager();
	pShaderMgr_ = new ShaderManager();

	HRESULT hr;
	if( FAILED( hr = D3DXCreateFont( pD3DDevice_, 15, 0, FW_BOLD, 1, FALSE, DEFAULT_CHARSET, 
		OUT_DEFAULT_PRECIS, DEFAULT_QUALITY, DEFAULT_PITCH | FF_DONTCARE, 
		L"Arial", &pFont_ ) ) )
	{
	    std::wstring str = DXGetErrorString9( hr );
		Logger::Log( LOGGING, str+L"CreateFont" );
	}

	if( FAILED( hr = D3DXCreateSprite( pD3DDevice_, &pSprite_ ) ) )
	{
	    std::wstring str = DXGetErrorString9( hr );
		Logger::Log( LOGGING,str+L"CreateSpriteFont" );
	}

//	D3DVIEWPORT9 viewport;
//	GraphicEngine::GetDXDevice()->GetViewport( &viewport );
//	viewport.Y = 30;
//	viewport.Height -= viewport.Y*2;
	pD3DDevice_->Clear( 0, 0, D3DCLEAR_TARGET, 0, 1.f, 0.f );
	pD3DDevice_->BeginScene();
	pD3DDevice_->EndScene();
	pD3DDevice_->Present( 0,0,0,0 );
//	GraphicEngine::GetDXDevice()->SetViewport( &viewport );
}

FrontEnd::~FrontEnd()
{
	if( pSprite_ )
		pSprite_->Release();
	if( pFont_ )
		pFont_->Release();
	delete pTexMgr_;
	delete pShaderMgr_;
	IDirect3D9* pD3D;
	pD3DDevice_->GetDirect3D( &pD3D );
	pD3DDevice_->Release();
	pD3D->Release();
	pD3D->Release();	
}

void FastMatrixInverse(D3DXMATRIX& ret, const D3DXMATRIX &m )
{
	D3DXMatrixIdentity( &ret );
	// rotation
	ret( 0, 0 ) = m( 0, 0 );
	ret( 0, 1 ) = m( 1, 0 );
	ret( 0, 2 ) = m( 2, 0 );
	ret( 1, 0 ) = m( 0, 1 );
	ret( 1, 1 ) = m( 1, 1 );
	ret( 1, 2 ) = m( 2, 1 );
	ret( 2, 0 ) = m( 0, 2 );
	ret( 2, 1 ) = m( 1, 2 );
	ret( 2, 2 ) = m( 2, 2 );

	// translation
	//	ret( 3, 0 ) = -m( 3, 0 );
	//	ret( 3, 1 ) = -m( 3, 1 );
	//	ret( 3, 2 ) = -m( 3, 2 );
	//
	//	ret._41 = 0.f;
	//	ret._42 = 0.f;
	//	ret._43 = 0.f;
	//	ret._14 = 0.f;
	//	ret._24 = 0.f;
	//	ret._34 = 0.f;
	//	ret._44 = 1.f;
	//
} // end MatrixInverse

void FrontEnd::SetWorldTransform( const D3DXMATRIX& mat )
{
	matWorld_ = mat;
	pD3DDevice_->SetTransform( D3DTS_WORLD, (D3DMATRIX*)(&mat) );
}
void FrontEnd::SetViewTransform( const D3DXMATRIX& mat )
{
	matView_ = mat;
	FastMatrixInverse( matInv_, matView_  );

	pD3DDevice_->SetTransform( D3DTS_VIEW, (D3DMATRIX*)(&mat) );
}

const D3DXMATRIX& FrontEnd::GetInvViewTransform() const
{
	return matInv_;
}

void FrontEnd::SetProjTransform( const D3DXMATRIX& mat )
{
	matProj_ = mat;
	pD3DDevice_->SetTransform( D3DTS_PROJECTION, (D3DMATRIX*)(&mat) );
}
void FrontEnd::BeginScene()
{
	if( bDeviceLost_ )
		return;
	pD3DDevice_->BeginScene();
	++nbrFrames_;
}
void FrontEnd::EndScene()
{
	if( bDeviceLost_ )
		return;
	RenderText();
	pD3DDevice_->EndScene();
}
void FrontEnd::Present()
{
	if( bDeviceLost_ )
		return;
	HRESULT hr = pD3DDevice_->Present( 0,0,0,0 );
	if( FAILED( hr ) )
	{
		bDeviceLost_ = true;
		//LOG_WARN( DXGetErrorString9( hr ) );
	    std::wstring str = DXGetErrorString9( hr );
		Logger::Log( LOGGING, str+L"Present" );
		
	}
}
void FrontEnd::Clear( DWORD dwFlags, const D3DCOLOR& color, float rZ, DWORD dwStencil )
{
	if( bDeviceLost_ )
	{
		HRESULT hr;
		hr = pD3DDevice_->TestCooperativeLevel();
		if( FAILED( hr ) )
		{
			if( D3DERR_DEVICELOST == hr )
			{
				// The device has been lost but cannot be reset at this time.  
				// So wait until it can be reset.
				return;
			}
		}
		//LOG_INFO( "Start reseting device" );
		// OnLostDevice
		hr = pFont_->OnLostDevice();
		if( FAILED( hr ) )
		{
			//LOG_ERROR( DXGetErrorString9( hr ) );
    	    std::wstring str = DXGetErrorString9( hr );
    		Logger::Log( LOGGING, str+L"OnLostDevice" );
			
		}
		pShaderMgr_->OnLostDevice();
		pSprite_->Release();
		pSprite_ = 0;

		Detail::ZeroedMemory< D3DPRESENT_PARAMETERS > d3dpp;
		d3dpp.Windowed = false;
		d3dpp.SwapEffect = D3DSWAPEFFECT_DISCARD;
		d3dpp.BackBufferFormat = D3DFMT_UNKNOWN;
		d3dpp.EnableAutoDepthStencil = TRUE;
		d3dpp.AutoDepthStencilFormat = D3DFMT_D24X8;
		d3dpp.BackBufferFormat = D3DFMT_X8R8G8B8;
		d3dpp.BackBufferWidth = 1024;
		d3dpp.BackBufferHeight = 768;

		hr = pD3DDevice_->Reset( &d3dpp );
		if( FAILED( hr ) )
		{
			//LOG_ERROR( DXGetErrorString9( hr ) );
    	    std::wstring str = DXGetErrorString9( hr );
    		Logger::Log( LOGGING, str+L"Reset" );
		}
		// OnResetDevice
		hr = pFont_->OnResetDevice();
		if( FAILED( hr ) )
		{
			//LOG_ERROR( DXGetErrorString9( hr ) );
    	    std::wstring str = DXGetErrorString9( hr );
    		Logger::Log( LOGGING, str+L"ResetDevice" );
		}
		pShaderMgr_->OnResetDevice();
		hr = D3DXCreateSprite( pD3DDevice_, &pSprite_ );
		if( FAILED( hr ) )
		{
			//LOG_ERROR( DXGetErrorString9( hr ) );
    	    std::wstring str = DXGetErrorString9( hr );
    		Logger::Log( LOGGING, str+L"CreateSprite" );
		}
		bDeviceLost_ = false;
		//LOG_INFO( "Reset device ok" );
	}

	pD3DDevice_->Clear( 0, 0, dwFlags, color, rZ, dwStencil );
}

Texture* FrontEnd::GetTexture( const std::wstring& strTextureName )
{
	return pTexMgr_->GetTexture( strTextureName );
}

Shader* FrontEnd::GetEffect( const std::wstring& strEffectName )
{
	return pShaderMgr_->GetEffect( strEffectName );
}

void FrontEnd::RenderText()
{
	Detail::TextHelper txtHelper( pFont_, pSprite_, 15 );

	// Output statistics
	txtHelper.Begin();
	txtHelper.SetInsertionPos( 2, 0 );
	txtHelper.SetForegroundColor( D3DXCOLOR( 1.0f, 1.0f, 0.0f, 1.0f ) );
	//txtHelper.DrawFormattedTextLine( L"FPS : %02d", nbrFramesPerSecond_ );

	txtHelper.End();

}

void FrontEnd::WriteInfo( const std::wstring& strInfo )
{
	Detail::TextHelper txtHelper( pFont_, pSprite_, 15 );

	// Output statistics
	txtHelper.Begin();
	txtHelper.SetInsertionPos( 2, 10 );
	txtHelper.SetForegroundColor( D3DXCOLOR( 1.0f, 1.0f, 0.0f, 1.0f ) );
	txtHelper.DrawFormattedTextLine( strInfo.c_str() );
	txtHelper.End();
}

void FrontEnd::ComputeFPS()
{
	nbrFramesPerSecond_ = nbrFrames_;
	nbrFrames_ = 0 ;
}

D3DXVECTOR3 FrontEnd::Unproject( const D3DXVECTOR2& vScreen ) const
{
	D3DXVECTOR3 v;
	v.x = vScreen.x;
	v.y = vScreen.y;
	v.z = 1.f;
	D3DVIEWPORT9 viewport;
	pD3DDevice_->GetViewport( &viewport );
	D3DXVECTOR3 vOut;
	D3DXMATRIX mat;
	D3DXMatrixIdentity( &mat );
	D3DXVec3Unproject( &vOut, &v, &viewport, &matProj_, &matView_, &mat );
	return vOut;
}
}
