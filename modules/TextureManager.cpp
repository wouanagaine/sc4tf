#include "TextureManager.h"
#include "FrontEnd.h"
#include "Logger.h"
#include <map>

#include <DX/D3DX9.h>
#include <dx/dxerr9.h>
//#include "VirtualFileSystem/VirtualFileSystem.h"
#include "MemBuff.h"

namespace GraphicEngine
{

	class Texture
	{
		friend IDirect3DBaseTexture9* ToDX( const Texture& tex );
		IDirect3DBaseTexture9* pDXTex_;

	public:
		Texture()
			: pDXTex_( 0 )
		{
		}
		Texture( const Texture& rhs )
			: pDXTex_( rhs.pDXTex_ )
		{
			if( pDXTex_ )
				pDXTex_->AddRef();
		}
		Texture& operator=( const Texture& rhs )
		{
			if( this == &rhs )
				return *this;

			if( pDXTex_ )
				pDXTex_->Release();
			if( rhs.pDXTex_ )
				rhs.pDXTex_->AddRef();
			pDXTex_ = rhs.pDXTex_;
			return *this;
		}
		explicit Texture( IDirect3DBaseTexture9* pDXTex )
			: pDXTex_( pDXTex )
		{
		}
		~Texture()
		{
			if( pDXTex_ )
				pDXTex_->Release();
		}
	};

	struct TextureManagerImpl
	{
		TextureManagerImpl()
			: frontEnd_( FrontEnd::Ref() )
			, textures_()
		{

		}
		~TextureManagerImpl()
		{
			textures_.clear();
		}
	
		FrontEnd& frontEnd_;
		std::map< std::wstring, Texture > textures_;
	};

	TextureManager::TextureManager()
		: pImpl_( new TextureManagerImpl() )
	{
	}
	TextureManager::~TextureManager()
	{
		delete pImpl_;
	}

	Texture* TextureManager::GetTexture( const std::wstring& strTexName )
	{
		IDirect3DBaseTexture9* pBaseTex = 0;
		std::map< std::wstring, Texture >::iterator itFound = pImpl_->textures_.find( strTexName );
		if( itFound != pImpl_->textures_.end() )
			return &itFound->second;

		VFS::MemoryBuffer memBuff;
		VFS::ReadWhole( strTexName, memBuff );

		

		D3DXIMAGE_INFO info;
		HRESULT hr =D3DXGetImageInfoFromFileInMemory( memBuff.pBuffer, (UINT)memBuff.nSize,  &info );
        if( FAILED( hr ) )
            Logger::Log( LOGGING,std::wstring( DXGetErrorString9( hr ) ) + L"D3DXGetImageInfoFromFileInMemory" );
		if( info.ResourceType == D3DRTYPE_TEXTURE )
		{
			IDirect3DTexture9* pTex = 0;
			if( FAILED( hr =D3DXCreateTextureFromFileInMemory( pImpl_->frontEnd_.pD3DDevice_, memBuff.pBuffer,  (UINT)memBuff.nSize, &pTex ) ) )
			{
			    
//				LOG_ERROR( L"Failed reading normal texture "+ strTexName );
				printf( "Failed reading normal texture\n");
				Logger::Log( LOGGING, std::wstring( DXGetErrorString9( hr ) ) + L"D3DXCreateTextureFromFileInMemory" );
				return 0;
			}
//			LOG_INFO( L"Successfully reading normal texture "+ strTexName );
			//printf( "Successfully reading normal texture \n");
			
			pBaseTex = pTex;
		}
		else if( info.ResourceType == D3DRTYPE_CUBETEXTURE )
		{
			IDirect3DCubeTexture9* pTex = 0;
			if( FAILED( D3DXCreateCubeTextureFromFileInMemory( pImpl_->frontEnd_.pD3DDevice_, memBuff.pBuffer,  (UINT)memBuff.nSize, &pTex ) ) )
			{
//				LOG_ERROR( L"Failed reading cube texture "+ strTexName );
				Logger::Log( LOGGING, std::wstring( DXGetErrorString9( hr ) ) + L"D3DXCreateCubeTextureFromFileInMemory" );
				return 0;
			}
//			LOG_INFO(  L"Successfully reading cube texture "+ strTexName );
			pBaseTex = pTex;

		}
		else if( info.ResourceType == D3DRTYPE_VOLUMETEXTURE )
		{
			IDirect3DVolumeTexture9* pTex = 0;
			if( FAILED( D3DXCreateVolumeTextureFromFileInMemory( pImpl_->frontEnd_.pD3DDevice_, memBuff.pBuffer,  (UINT)memBuff.nSize, &pTex ) ) )
			{
//				LOG_ERROR( L"Failed reading volume texture "+ strTexName );
				Logger::Log( LOGGING, std::wstring( DXGetErrorString9( hr ) )+ L"D3DXCreateVolumeTextureFromFileInMemory" );
				return 0;
			}
//			LOG_INFO( L"Successfully reading volume texture "+ strTexName );
			pBaseTex = pTex;

		}

		pImpl_->textures_[ strTexName ] = Texture( pBaseTex );
		return &pImpl_->textures_[ strTexName ];

	}
	void TextureManager::FreeAllTextures()
	{
		pImpl_->textures_.clear();
	}

	IDirect3DBaseTexture9* ToDX( const Texture& tex )
	{
		return tex.pDXTex_;
	}
}
