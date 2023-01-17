#ifndef Shader_included
#define Shader_included

#include <dx/d3dx9.h>
#include <string>
#include <map>

namespace GraphicEngine
{

class Shader
{
	friend class ShaderManager;

	ID3DXEffect* pDXEffect_;
	D3DXEFFECT_DESC effectDesc_;

	D3DXHANDLE matWorldEffectHandle_;
	D3DXHANDLE matViewEffectHandle_;
	D3DXHANDLE matInvViewEffectHandle_;
	D3DXHANDLE matProjEffectHandle_;
	D3DXHANDLE matWorldViewEffectHandle_;
	D3DXHANDLE matViewProjEffectHandle_;
	D3DXHANDLE matWorldViewProjEffectHandle_;
	D3DXHANDLE timeHandle_;
	D3DXHANDLE textureHandle_;

	Shader( const Shader& );
	Shader& operator=( const Shader& );

public:
	explicit Shader()
	{
		memset( this, 0, sizeof( Shader ) );
	}
	~Shader()
	{
		if( pDXEffect_ )
			pDXEffect_->Release();
	}
	UINT Begin();
	void BeginPass( UINT nPass )
	{
		pDXEffect_->BeginPass( nPass );
		pDXEffect_->CommitChanges();
	}
	void EndPass()
	{
		pDXEffect_->EndPass();
	}
	void End()
	{
		pDXEffect_->End();
	}

	void SetValue( const std::string& strParam, float rVal )
	{
		D3DXHANDLE h = pDXEffect_->GetParameterByName( 0, strParam.c_str() );
		pDXEffect_->SetFloat( h, rVal );
	}
	void SetTexture( const std::wstring& strTexFile );

};

class ShaderManager
{
	std::map< std::wstring, Shader* > effects_;

	ShaderManager( const ShaderManager& );
	ShaderManager& operator=( const ShaderManager& );

public:
	explicit ShaderManager();
	~ShaderManager();

	void OnLostDevice();
	void OnResetDevice();
	Shader* GetEffect( const std::wstring& strEffectName );
};

}
#endif Shader_included