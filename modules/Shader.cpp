#include "Shader.h"
#include "FrontEnd.h"
#include "TextureManager.h"
#include <windows.h>
#include "Logger.h"

//#include "VirtualFileSystem/VirtualFileSystem.h"
//#include "Logger/Logger.h"
#include <dx/dxerr9.h>
#include "MemBuff.h"

namespace GraphicEngine
{

	void Shader::SetTexture( const std::wstring& strTexFile )
	{
		if( textureHandle_ != 0 )
			pDXEffect_->SetTexture( textureHandle_, ToDX( *FrontEnd::Ref().GetTexture( strTexFile ) ) );
	}

ShaderManager::ShaderManager()
: effects_()
{

}

ShaderManager::~ShaderManager()
{
	std::map< std::wstring, Shader* >::iterator it = effects_.begin();
	std::map< std::wstring, Shader* >::iterator itEnd = effects_.end();

	while( it != itEnd )
	{
		delete it->second;
		++it;
	}
}

Shader* ShaderManager::GetEffect( const std::wstring& strEffectName )
{
	std::map< std::wstring, Shader* >::iterator itFound = effects_.find( strEffectName );
	if( itFound != effects_.end() )
		return itFound->second;

    HRESULT hr;
	Shader* pShader = new Shader();
	LPD3DXBUFFER pBufferErrors = NULL;
	VFS::MemoryBuffer memBuff;
	VFS::ReadWhole( strEffectName, memBuff );
	if( FAILED( hr = D3DXCreateEffect( GetDXDevice(), memBuff.pBuffer, (UINT)memBuff.nSize, NULL, NULL, D3DXSHADER_DEBUG, NULL, &pShader->pDXEffect_, &pBufferErrors ) ) )
	{
		Logger::Log( LOGGING, std::wstring( DXGetErrorString9( hr ) ) + L"D3DXCreateEffect" );
		//LOG_ERROR( L"Failed reading shader effect "+ strEffectName );
		printf( "Failed reading shader effect ");
		if( pBufferErrors )
		{
			OutputDebugStringA( (CHAR*)pBufferErrors->GetBufferPointer() );
			std::string strerror = (CHAR*)pBufferErrors->GetBufferPointer();
			//LOG_ERROR( strerror );
			printf( "%s\n",strerror.c_str() );
			
			pBufferErrors->Release();
			throw std::runtime_error( "ShaderManager");
		}
		return 0;
	}
	//LOG_INFO( L"Successfully reading shader effect "+ strEffectName );
	pShader->pDXEffect_->GetDesc( &pShader->effectDesc_ );
	LPCWSTR pname = 0;	
	std::wstring strName;
	strName = L"";
	//Recupere les handles connus
	for( UINT iParam = 0; iParam < pShader->effectDesc_.Parameters; iParam++ )
	{
		D3DXHANDLE hParam;
		D3DXPARAMETER_DESC ParamDesc;
		hParam = pShader->pDXEffect_->GetParameter ( NULL, iParam );
		pShader->pDXEffect_->GetParameterDesc( hParam, &ParamDesc );

		if( ParamDesc.Semantic == NULL && ParamDesc.Type == D3DXPT_STRING )
		{
//			if( strcmpi( ParamDesc.Name, "name" ) == 0 )
//			{
//				pShader->pDXEffect_->GetString( "name", &pname);
//				strName = pname;
//			}
		}
		if( ParamDesc.Semantic != NULL && ParamDesc.Type == D3DXPT_FLOAT )
		{
			if( strcmpi( ParamDesc.Semantic, "time" ) == 0 )
			{
				pShader->timeHandle_ = hParam;	
			}
		}
		if( ParamDesc.Semantic != NULL && 
			( ParamDesc.Class == D3DXPC_MATRIX_ROWS || ParamDesc.Class == D3DXPC_MATRIX_COLUMNS ) )
		{
			if( strcmpi( ParamDesc.Semantic, "world" ) == 0 )
				pShader->matWorldEffectHandle_ = hParam;
			else if( strcmpi( ParamDesc.Semantic, "view" ) == 0 )
				pShader->matViewEffectHandle_ = hParam;
			else if( strcmpi( ParamDesc.Semantic, "invview" ) == 0 )
				pShader->matInvViewEffectHandle_ = hParam;
			else if( strcmpi( ParamDesc.Semantic, "projection" ) == 0 )
				pShader->matProjEffectHandle_ = hParam;
			else if( strcmpi( ParamDesc.Semantic, "worldview" ) == 0 )
				pShader->matWorldViewEffectHandle_ = hParam;
			else if( strcmpi( ParamDesc.Semantic, "viewprojection" ) == 0 )
				pShader->matViewProjEffectHandle_ = hParam;
			else if( strcmpi( ParamDesc.Semantic, "worldviewprojection" ) == 0 )
				pShader->matWorldViewProjEffectHandle_ = hParam;
		}
		LPCSTR pstrName = NULL;
		for( UINT iAnnot = 0; iAnnot < ParamDesc.Annotations; iAnnot++ )
		{
			D3DXHANDLE hAnnot;
			D3DXPARAMETER_DESC AnnotDesc;

			hAnnot = pShader->pDXEffect_->GetAnnotation ( hParam, iAnnot );
			pShader->pDXEffect_->GetParameterDesc( hAnnot, &AnnotDesc );
			if( strcmpi( AnnotDesc.Name, "name" ) == 0 )
			{
				pShader->pDXEffect_->GetString( hAnnot, &pstrName );
				if( !strcmpi( pstrName, "$0" ) )
					pShader->textureHandle_ = hParam;
				else
				{
					WCHAR strName[MAX_PATH];
					MultiByteToWideChar( CP_ACP, 0, pstrName, -1, strName, MAX_PATH );
					pShader->pDXEffect_->SetTexture( hParam, ToDX( *FrontEnd::Ref().GetTexture( strName ) ) );
				}

			}
		}

	}

	D3DXHANDLE tec;
	//pShader->pDXEffect_->FindNextValidTechnique( "tec", &tec );
	tec = pShader->pDXEffect_->GetTechnique( 0 );
	if( SUCCEEDED( hr = pShader->pDXEffect_->ValidateTechnique( tec ) ) )
	{

		pShader->pDXEffect_->SetTechnique( tec );
	}
	else
	{
		//Logger::Log( DXGetErrorString9( hr ) );
		Logger::Log( LOGGING, std::wstring( DXGetErrorString9( hr ) ) + L"ValidateTec" );
		hr = pShader->pDXEffect_->SetTechnique( pShader->pDXEffect_->GetTechnique( 1 ) );
		if( FAILED( hr ) )
			Logger::Log( LOGGING, std::wstring( DXGetErrorString9( hr ) ) + L"ValidateTec FP" );
	}

	effects_[ strEffectName ] = pShader;
	return pShader;

}
/*
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
*/

UINT Shader::Begin()
	{
	FrontEnd& fe = FrontEnd::Ref();
	if( matProjEffectHandle_ )
		pDXEffect_->SetMatrix( matProjEffectHandle_, &fe.matProj_ );

	if( matWorldEffectHandle_ )
		pDXEffect_->SetMatrix( matWorldEffectHandle_, &fe.matWorld_ );

	if( matViewEffectHandle_ )
		pDXEffect_->SetMatrix( matViewEffectHandle_, &fe.matView_ );

	if( matInvViewEffectHandle_ )
	{
		pDXEffect_->SetMatrix( matInvViewEffectHandle_, &fe.matInv_ );
	}

	if( matWorldViewEffectHandle_ )
	{
		D3DXMATRIX matWorldView = fe.matWorld_ * fe.matView_;
		pDXEffect_->SetMatrix( matWorldViewEffectHandle_, &matWorldView );
	}

	if( matWorldViewProjEffectHandle_ )
	{
		D3DXMATRIX matWorldView = fe.matWorld_ * fe.matView_ * fe.matProj_;
		pDXEffect_->SetMatrix( matWorldViewProjEffectHandle_, &matWorldView );
	}


	UINT nPass;
	HRESULT hr = pDXEffect_->Begin( &nPass, 0 );
	if( FAILED( hr ) )

        Logger::Log( LOGGING, std::wstring( DXGetErrorString9( hr ) ) + L"BeginEffect" );
	return nPass;
}

	void ShaderManager::OnLostDevice()
	{
		std::map< std::wstring, Shader* >::iterator it = effects_.begin();
		std::map< std::wstring, Shader* >::iterator itEnd = effects_.end();

		while( it != itEnd )
		{
			it->second->pDXEffect_->OnLostDevice();
			++it;
		}
	}
	void ShaderManager::OnResetDevice()
	{
		std::map< std::wstring, Shader* >::iterator it = effects_.begin();
		std::map< std::wstring, Shader* >::iterator itEnd = effects_.end();

		while( it != itEnd )
		{
			it->second->pDXEffect_->OnResetDevice();
			++it;
		}
	}

}
