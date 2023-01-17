////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////
#include <python.h>
#include <dx/d3d9.h>
#include <dx/dxerr9.h>
#include "FrontEnd.h"
#include "Shader.h"
#include "Camera.h"
#include "Culling.h"
#include "TextureManager.h"
#include "Logger.h"
#include <vector>
#include <utility>
#include <shlobj.h>
#include <sstream>
#include <iostream>
#pragma comment( lib,"d3d9.lib" )
#pragma comment( lib,"d3dx9.lib" )
#pragma comment( lib,"DxErr9.lib" )
#pragma comment( lib,"user32.lib" )
#pragma comment( lib,"shell32.lib" )
namespace GraphicEngine

{
	inline 
	int clamp( int v, int a0, int a2 )
	{
	    if( v < a0 )
	        return a0;
	    if( v > a2 )
	        return a2;
	    return v;
	}

	const int chunkSize = 33;
	Camera g_Camera;
typedef std::pair< IDirect3DVertexBuffer9*, DWORD > DXMeshVB;

	struct ChunkVertex
	{
		D3DXVECTOR3 vPos_;
		D3DCOLOR diffuse_;
		D3DXVECTOR2 uv_;
	};

	bool g_bWired = false;
	class Chunk
	{
		friend class Terran;
		BBox bbox_;
		DXMeshVB dxData_;
		DXMeshVB dxWater_;
		//D3DXVECTOR3 vPos_;
		//GraphicEngine::E_VisState eVisState_;
		int chunkSize_;
		//std::wstring strAssociatedTex_;
	public:
		explicit Chunk( /*const std::wstring& strAssociatedTex, */DXMeshVB& dxData, DXMeshVB& dxWater, int chunkSize, const BBox& bbox )
			: dxData_( dxData )
			, bbox_( bbox )
			//, eVisState_( GraphicEngine::eVisState_Unknown )
			//, vPos_( vPos )
			, chunkSize_( chunkSize )
			, dxWater_( dxWater )
			//, strAssociatedTex_( strAssociatedTex )
		{
		}
		~Chunk()
		{
			dxData_.first->Release();
			dxWater_.first->Release();
		}
		void Render(IDirect3DIndexBuffer9* pIB, IDirect3DVertexDeclaration9* pvtxDecl)
		{
			if( g_Camera.GetFrustrum().CullBBox( bbox_ ) == Culling::eCullingFullOutside )
				return;

            HRESULT hr;
			hr = GraphicEngine::GetDXDevice()->SetVertexDeclaration( pvtxDecl );
			if( FAILED(hr ) )
				Logger::Log( LOGGING, std::wstring( DXGetErrorString9( hr ) ) + L"SetVertexDecl" );
	
			hr = GraphicEngine::GetDXDevice()->SetFVF( D3DFVF_XYZ|D3DFVF_DIFFUSE|D3DFVF_TEX1);
			if( FAILED(hr ) )
				Logger::Log( LOGGING, std::wstring( DXGetErrorString9( hr ) ) + L"SetFVF" );

			// Set the stream sources that the vertex declaration will point to
			hr = GraphicEngine::GetDXDevice()->SetStreamSource(0, dxData_.first, 0, sizeof(ChunkVertex));	// set to first keyframe
			if( FAILED(hr ) )
                Logger::Log( LOGGING, std::wstring( DXGetErrorString9( hr ) ) + L"SetStreamSource" );
			hr = GraphicEngine::GetDXDevice()->SetIndices( pIB );							// index buffer
			if( FAILED(hr ) )
                Logger::Log( LOGGING, std::wstring( DXGetErrorString9( hr ) ) + L"SetIndices" );
			Shader& shader= *FrontEnd::Ref().GetEffect( g_bWired ? L"datas/landWired.fx":L"datas/land.fx");	


			UINT nPass = shader.Begin();
			//shader.SetTexture( strAssociatedTex_ );
			for( UINT32 p = 0 ; p < nPass; ++p ) 					
			{
				shader.BeginPass( p );
				/*for( int i = 0; i < chunkSize_-1;++i )
				{
					hr = GraphicEngine::GetDXDevice()->DrawIndexedPrimitive(D3DPT_TRIANGLESTRIP, i*chunkSize_, 0, chunkSize_*2, 0, (chunkSize_-1)*2 );
        			if( FAILED(hr ) )
                        Logger::Log( LOGGING, std::wstring( DXGetErrorString9( hr ) ) + L"DIP" );
				}*/
				hr = GraphicEngine::GetDXDevice()->DrawIndexedPrimitive(D3DPT_TRIANGLESTRIP, 0, 0, chunkSize_*chunkSize_, 0, (chunkSize*2+1)*(chunkSize-1)-3 );
        		if( FAILED(hr ) )
                    Logger::Log( LOGGING, std::wstring( DXGetErrorString9( hr ) ) + L"DIP" );
				shader.EndPass();

			}
			shader.End();	
		}

		void RenderWater( IDirect3DVertexDeclaration9* pvtxDecl)
		{
			if( g_Camera.GetFrustrum().CullBBox( bbox_ ) == Culling::eCullingFullOutside )
				return;
			// draw water tile
			{
			    HRESULT hr;
				GraphicEngine::GetDXDevice()->SetFVF( D3DFVF_XYZ|D3DFVF_DIFFUSE|D3DFVF_TEX1);
				hr = GraphicEngine::GetDXDevice()->SetVertexDeclaration( pvtxDecl );
    			if( FAILED(hr ) )
                    Logger::Log( LOGGING, std::wstring( DXGetErrorString9( hr ) ) + L"SetVertexDecl" );
				hr = GraphicEngine::GetDXDevice()->SetStreamSource(0, dxWater_.first, 0, sizeof(ChunkVertex));	// set to first keyframe
    			if( FAILED(hr ) )
                    Logger::Log( LOGGING, std::wstring( DXGetErrorString9( hr ) ) + L"SetStreamSource" );
				hr = GraphicEngine::GetDXDevice()->SetIndices( 0 );							// index buffer
    			if( FAILED(hr ) )
                    Logger::Log( LOGGING, std::wstring( DXGetErrorString9( hr ) ) + L"SetIndices" );
				Shader& shader= *FrontEnd::Ref().GetEffect( L"datas/water.fx");	

				UINT nPass = shader.Begin();
				for( UINT32 p = 0 ; p < nPass; ++p ) 					
				{
					shader.BeginPass( p );
					hr = GraphicEngine::GetDXDevice()->DrawPrimitive(D3DPT_TRIANGLESTRIP, 0, 2 );
        			if( FAILED(hr ) )
                        Logger::Log( LOGGING, std::wstring( DXGetErrorString9( hr ) ) + L"DP" );
					shader.EndPass();
					//printf( "Draw water\n");

				}
				shader.End();

			}
		}
	};

	class Terran
	{
		float* pHeight_;
		unsigned char* rgb_;
		int sizeX_;
		int sizeY_;
		float rWaterLevel_;
		std::vector< Chunk* > chunks_;
		IDirect3DVertexDeclaration9* pvtxDecl_;
		IDirect3DIndexBuffer9* pIB_;
	public:
		Terran( float rWaterLevel, int sizeX,int sizeY, float* pHeight, unsigned char* rgb );
		~Terran( )
		{
			std::vector< Chunk* >::iterator it = chunks_.begin();
			std::vector< Chunk* >::iterator itEnd = chunks_.end();
			while( it != itEnd )
			{
				delete *it;
				++it;
			};
			chunks_.clear();
			pvtxDecl_->Release();
			pIB_->Release();
			pvtxDecl_ = 0;
			pIB_ = 0;
			delete[] pHeight_ ;
			pHeight_ = 0;
			delete[] rgb_;
			rgb_ = 0;
		}
		void UpdateHeight( float* pHeight, float waterLevel,int left, int top, int right, int bottom );
		void UpdateRGB( unsigned char* rgb );
		void UpdateWater( float waterLevel );
		void Draw( bool bRenderWater);
		void UpdateVB( int left, int top, int right, int bottom, bool bOnlyColor );
		void UpdateColor( int cX, int cY, Chunk* pChunk );
		void UpdateHeight( int cX, int cY, Chunk* pChunk );
		Chunk* CreateOne( int cX, int cY );

		D3DXVECTOR3 Intersect( const D3DXVECTOR3& vFrom, const D3DXVECTOR3& vDir )const;
		float HeightInWorld( const D3DXVECTOR3& v ) const;

		float GetHeight( int x, int y )
		{
			x = abs( x ) % sizeX_;					// Error check our x value
			y = abs( y ) % sizeY_;					// Error check our y value
			return pHeight_[x + (y * sizeX_)];		// Index into our height array and return the height
		}
	};
	Terran* g_pTerran = NULL;
	D3DCOLOR g_bgcolor = 0x102080;

	class MouseRep
	{
		ID3DXSprite* pSprite_;
		IDirect3DTexture9* pTex_;
		int radius_;
		bool bSquared_;
	public:
		MouseRep()
			: pSprite_( 0 )
			, pTex_( (IDirect3DTexture9*)GraphicEngine::ToDX( *GraphicEngine::FrontEnd::Ref().GetTexture( L"datas/mouse.tga" ) ) )
			, radius_( 5 )
			, bSquared_( false) 
		{
			HRESULT hr;
			hr = D3DXCreateSprite( GraphicEngine::GetDXDevice(), &pSprite_ );

			if( FAILED( hr ) )
			{
				Logger::Log( LOGGING, std::wstring( DXGetErrorString9( hr ) ) + L"createsprite" );
			}
//			LOG_ERROR( DXGetErrorString9( hr ) );
		}
		~MouseRep()
		{
			pSprite_->Release();
		}

		D3DXVECTOR2 GetFloatVertexMouse( int mx, int my )
		{
			D3DXVECTOR3 v = g_Camera.GetPos();
			D3DXVECTOR3 vMouse = GraphicEngine::FrontEnd::Ref().Unproject( D3DXVECTOR2( mx,my ) );
			D3DXVECTOR3 vDir = vMouse -v;
			v = g_pTerran->Intersect( v, *D3DXVec3Normalize( &vDir, &vDir) );
			v/=12.f;
			return D3DXVECTOR2( v.x,v.z );
		}

		D3DXVECTOR2 GetVertexMouse( int mx, int my )
		{
			D3DXVECTOR3 v = g_Camera.GetPos();
			D3DXVECTOR3 vMouse = GraphicEngine::FrontEnd::Ref().Unproject( D3DXVECTOR2( mx,my ) );
			D3DXVECTOR3 vDir = vMouse -v;
			v = g_pTerran->Intersect( v, *D3DXVec3Normalize( &vDir, &vDir) );
			D3DXVECTOR3 v0 = (v+D3DXVECTOR3(6,0,6))/12.f;
			int x = v0.x;
			int z = v0.z;
			return D3DXVECTOR2( x,z );
		}
		void SetRadius( int nR )
		{
		    radius_ = nR;
		}
		void SetShape( bool bSquared )
		{
		    bSquared_ = bSquared;
		}
		void Render( int mx, int my )
		{
			/*D3DXVECTOR3 v = g_Camera.GetPos();
			D3DXVECTOR3 vMouse = GraphicEngine::FrontEnd::Ref().Unproject( D3DXVECTOR2( mx,my ) );
			D3DXVECTOR3 vDir = vMouse -v;
			v = g_pTerran->Intersect( v, *D3DXVec3Normalize( &vDir, &vDir) );*/
			D3DXVECTOR3 v( mx*12, g_pTerran->GetHeight( mx,my ), my*12  );

			pSprite_->SetWorldViewRH( 0, &GraphicEngine::FrontEnd::Ref().GetViewTransform() );
			pSprite_->Begin( D3DXSPRITE_BILLBOARD|D3DXSPRITE_OBJECTSPACE);	
			GetDXDevice()->SetRenderState( D3DRS_ZWRITEENABLE, D3DZB_FALSE );
			GetDXDevice()->SetRenderState( D3DRS_ZENABLE, D3DZB_FALSE );
			//pSprite_->SetTransform(  );
			D3DXVECTOR3 vCenter;
			vCenter.x = 1;
			vCenter.y = 3;
			vCenter.z = 0;

			D3DXVECTOR3 v0 = (v+D3DXVECTOR3(6,0,6))/12.f;
			int x = v0.x;
			int z = v0.z;
			if( !pTex_ )
				printf("erreur tex" );
			RECT rcTex = { 0, 0, 3, 3  };
			int radiusEffect = radius_;
			float h = g_pTerran->GetHeight( x,z ) +3;
			D3DCOLOR colors[] = {
				D3DCOLOR_RGBA( 0x3F,0x7F,0xFF, 0x7f ),
				D3DCOLOR_RGBA( 0x0,0x0,0x00, 0x7f ),
				D3DCOLOR_RGBA( 0x0,0x0,0xFF, 0x7f ),
				D3DCOLOR_RGBA( 0,0xFF,0x00, 0x7f ),
				D3DCOLOR_RGBA( 0,0xFF,0xFF, 0x7f ),
				D3DCOLOR_RGBA( 0xFF,0x00,0x00, 0x7f ),
				D3DCOLOR_RGBA( 0xFF,0x00,0xFF, 0x7f ),
				D3DCOLOR_RGBA( 0xFF,0xFF,0x00, 0x7f ),
				D3DCOLOR_RGBA( 0xFF,0xFF,0xFF, 0x7f ),
			};
			int dirs[] = { 0,1,2,3,
				           8,0,4,
						   7,6,5 };
			D3DXVECTOR3 dirsV[] = { D3DXVECTOR3(0,0,0),D3DXVECTOR3(-1,0,-1),D3DXVECTOR3(0,0,-1),D3DXVECTOR3(0,0,1),
				           D3DXVECTOR3(-1,0,0),D3DXVECTOR3(0,0,0),D3DXVECTOR3(1,0,0),
						   D3DXVECTOR3(-1,0,1),D3DXVECTOR3(0,0,1),D3DXVECTOR3(1,0,1) };

			for( int j = -radiusEffect; j <= radiusEffect; ++j )
				for( int i = -radiusEffect; i <= radiusEffect; ++i )
				{
					float d = sqrtf( j*12*12*j+i*12*12*i );
					if( !bSquared_ && d >= radiusEffect*12 )
						continue;
					float y = g_pTerran->GetHeight( x+i,z+j )+3;					
					D3DXVECTOR3 vPos;
					
					vPos = D3DXVECTOR3( (x+i)*12,y,(z+j)*12) ;			
					HRESULT hr;
					if( j == 0 && i == 0 )
						hr = pSprite_->Draw( pTex_, &rcTex,&vCenter,&vPos,D3DCOLOR_RGBA( 0xFF, 0x0, 0x00, 0x7F ) );
					else
					{
						int dirMin = 0;
						D3DXVECTOR3 dirV=D3DXVECTOR3(0,0,0);
						float yMin = y;
						for( int b = -1, dir = 1; b<2; ++b )
							for( int a = -1; a < 2; ++a,++dir )
							{
								float y1 = g_pTerran->GetHeight( x+i+a,z+j+b )+3;
								if( y1 < y && y1 < yMin )
								{
									yMin = y1;
									dirMin = dirs[dir];
									dirV = dirsV[dir];
									dirV.y = -fabs( y1-y)/12.f;
								}
							}

						D3DCOLOR color;
						if( y < h )
							color=D3DCOLOR_RGBA( 0x0, 0x0, 0xFF, 0x7F );
						else if( y > h )
							color=D3DCOLOR_RGBA( 0xFF, 0xFF, 0x7F, 0x7F );
						else
							color=D3DCOLOR_RGBA( 0x3F, 0x3F, 0x7F, 0x7F );

						for( int k = 0; k<1;++k )
						{
							D3DXVECTOR3 v = vPos+k*dirV;
							hr = pSprite_->Draw( pTex_, &rcTex,&vCenter,&v,color );
						}
/*
						if( y < h )
						{
							//int d = clamp( fabs( h-y ), 0, 0xFF );
							hr = pSprite_->Draw( pTex_, &rcTex,&vCenter,&vPos,D3DCOLOR_RGBA( 0x0, 0x0, 0xFF, 0x7F ) );
						}
						else if( y > h )
							hr = pSprite_->Draw( pTex_, &rcTex,&vCenter,&vPos,D3DCOLOR_RGBA( 0xFF, 0xFF, 0x7F, 0x7F ) );
						else
							hr = pSprite_->Draw( pTex_, &rcTex,&vCenter,&vPos,D3DCOLOR_RGBA( 0xFF, 0xFF, 0xFF, 0x7F ) );
							*/
					}
					if( FAILED( hr ) )
					{
						Logger::Log( LOGGING, std::wstring( DXGetErrorString9( hr ) ) + L"Draw" );
						printf( "erreur drawsprit" );
					}
				}
			pSprite_->End();
			GetDXDevice()->SetRenderState( D3DRS_ZWRITEENABLE, D3DZB_TRUE );
			GetDXDevice()->SetRenderState( D3DRS_ZENABLE, D3DZB_TRUE );
		}
	};
	MouseRep* g_pMouse = NULL;

	Terran::Terran( float rWaterLevel, int sizeX,int sizeY, float* pHeight, unsigned char* rgb )
		: sizeX_( sizeX )
		, sizeY_( sizeY )
		, pHeight_( new float[ sizeX*sizeY ] )
		, chunks_()
		, pvtxDecl_( 0 )
		, pIB_( 0 )
		, rWaterLevel_( rWaterLevel )
		, rgb_( new unsigned char[ sizeX*sizeY*3 ] )
	{
		
		memcpy( pHeight_, pHeight, sizeX*sizeY*sizeof(float) );
		memcpy( rgb_, rgb, sizeX*sizeY*3 );
		D3DVERTEXELEMENT9 vect_decl[] = 
		{
			{ 0, 0, D3DDECLTYPE_FLOAT3, D3DDECLMETHOD_DEFAULT, D3DDECLUSAGE_POSITION, 0 },
			{ 0, 3*sizeof(float), D3DDECLTYPE_D3DCOLOR, D3DDECLMETHOD_DEFAULT, D3DDECLUSAGE_COLOR, 0 },
			{ 0, 3*sizeof(float)+sizeof(D3DCOLOR), D3DDECLTYPE_FLOAT2, D3DDECLMETHOD_DEFAULT, D3DDECLUSAGE_TEXCOORD, 0 },
			D3DDECL_END() // this macro is always needed as the last item! DON'T FORGET ;)
		};
		HRESULT hr;
		hr = GraphicEngine::GetDXDevice()->CreateVertexDeclaration( vect_decl, &pvtxDecl_);
		if( FAILED( hr ) )
			Logger::Log( LOGGING, std::wstring( DXGetErrorString9( hr ) ) + L"CreateVertexDecl" );
		hr = GraphicEngine::GetDXDevice()->CreateIndexBuffer(sizeof(short)*(chunkSize*2+1)*(chunkSize-1),D3DUSAGE_WRITEONLY,D3DFMT_INDEX16,D3DPOOL_MANAGED,&pIB_,0);
		if( FAILED( hr ) )
			Logger::Log( LOGGING, std::wstring( DXGetErrorString9( hr ) ) + L"CreateIndexBuffer" );
		short* bufIdx = new short[ (chunkSize*2+1)*(chunkSize-1) ];
		short* pBuf = bufIdx;
		for( int j = 0; j < chunkSize-1; ++j )
		{ 
			if( (j&1) == 0 )
			{
				for( int i = 0; i < chunkSize; ++i )
				{
					*(pBuf++) = j*chunkSize+ i;
					*(pBuf++) = (j+1)*chunkSize+i;
				}
				*(pBuf++) = (j+1)*chunkSize+chunkSize-1;
			}
			else
			{
				for( int i = chunkSize-1; i >= 0; --i )
				{
					*(pBuf++) = j*chunkSize+i;
					*(pBuf++) = (j+1)*chunkSize+ i;
					
				}
				*(pBuf++) = (j+1)*chunkSize;
			}
		}
		void* data_ptr;
		pIB_->Lock(0, 0, &data_ptr, 0);
		memcpy(data_ptr, bufIdx, (chunkSize*2+1)*(chunkSize-1) * sizeof( short ) );
		pIB_->Unlock();
		delete[] bufIdx;

		int nbrChunkX = (sizeX_-1)/(chunkSize-1);
		int nbrChunkY = (sizeY_-1)/(chunkSize-1);

		//create each chunk
		chunks_.resize( nbrChunkX*nbrChunkY );
		//create each chunk
		for( int cY = 0; cY < nbrChunkY; ++cY )
		{
			for( int cX = 0; cX < nbrChunkX; ++cX )
			{
			    delete chunks_[ cX + cY*nbrChunkX ];
			    chunks_[ cX + cY*nbrChunkX ] = 0;
			    Chunk* pTemp = CreateOne( cX, cY );
			    if( pTemp )
                    chunks_[ cX + cY*nbrChunkX ] = pTemp;
				else
					printf("Error creating a VB\n" );
			}
		}
		//preload fx shader
		{
		Shader& shader= *FrontEnd::Ref().GetEffect( L"datas/land.fx");	
		shader.SetValue( "texSizeX", sizeX_ );
		shader.SetValue( "texSizeY", sizeY_ );
		}
		{
		Shader& shader= *FrontEnd::Ref().GetEffect( L"datas/landWired.fx");	
		shader.SetValue( "texSizeX", sizeX_ );
		shader.SetValue( "texSizeY", sizeY_ );
		}
		{
		Shader& shader= *FrontEnd::Ref().GetEffect( L"datas/water.fx");	
		shader.SetValue( "texSizeX", sizeX_ );
		shader.SetValue( "texSizeY", sizeY_ );
		}
	}
	void Terran::UpdateColor( int cX, int cY, Chunk* pChunk )
	{
		HRESULT hr;
		void* data_ptr;
		IDirect3DVertexBuffer9* pVB = pChunk->dxData_.first;
		hr = pVB->Lock(0, 0, &data_ptr,0);
		if( FAILED( hr ) )
			Logger::Log( LOGGING, std::wstring( DXGetErrorString9( hr ) ) + L"Lock height" );
		else
		{

			for( int y = 0; y < chunkSize; ++y )
				for( int x = 0; x < chunkSize; ++x )
				{
					int lx = x + cX*(chunkSize-1);
					int ly = y + cY*(chunkSize-1);
					//D3DXVECTOR3 v( lx*12,GetHeight( lx,ly ),ly*12 );
					ChunkVertex& cv = ((ChunkVertex*)data_ptr)[x+y*chunkSize];
					int r,g,b;
					r = rgb_[ (lx+ly*sizeX_)*3 ];
					g = rgb_[ (lx+ly*sizeX_)*3+1 ];
					b = rgb_[ (lx+ly*sizeX_)*3+2 ];
					cv.diffuse_ = D3DCOLOR_RGBA( r,g,b,255 );
				}

			pVB->Unlock();
		}
	}

	void Terran::UpdateHeight( int cX, int cY, Chunk* pChunk )
	{
		HRESULT hr;
		void* data_ptr;
		IDirect3DVertexBuffer9* pVB = pChunk->dxData_.first;
		hr = pVB->Lock(0, 0, &data_ptr,0);
		if( FAILED( hr ) )
			Logger::Log( LOGGING, std::wstring( DXGetErrorString9( hr ) ) + L"Lock height" );
		else
		{
			float demipixel = .5/65.f;
			for( int y = 0; y < chunkSize; ++y )
				for( int x = 0; x < chunkSize; ++x )
				{
					int lx = x + cX*(chunkSize-1);
					int ly = y + cY*(chunkSize-1);
					D3DXVECTOR3 v( lx*12,GetHeight( lx,ly ),ly*12 );
					pChunk->bbox_.ExpandBy( v );
					ChunkVertex& cv = ((ChunkVertex*)data_ptr)[x+y*chunkSize];
					cv.vPos_ = v;
				}

			pVB->Unlock();
		}
	}

	Chunk* Terran::CreateOne( int cX, int cY )
	{
		HRESULT hr;
	    void* data_ptr;
		BBox bbox;
		std::vector< ChunkVertex > buffer;
		std::vector< ChunkVertex > water;
		buffer.resize( chunkSize*chunkSize );
		water.resize( 4 );
		float demipixel = .5/65.f;
		for( int y = 0; y < chunkSize; ++y )
			for( int x = 0; x < chunkSize; ++x )
			{
				int lx = x + cX*(chunkSize-1);
				int ly = y + cY*(chunkSize-1);
				D3DXVECTOR3 v( lx*12,GetHeight( lx,ly ),ly*12 );
				bbox.ExpandBy( v );
				ChunkVertex cv;
				cv.vPos_ = v;
				cv.uv_ = D3DXVECTOR2( x,y);
				int r,g,b;
				r = rgb_[ (lx+ly*sizeX_)*3 ];
				g = rgb_[ (lx+ly*sizeX_)*3+1 ];
				b = rgb_[ (lx+ly*sizeX_)*3+2 ];
				cv.diffuse_ = D3DCOLOR_RGBA( r,g,b,255 );
				buffer[x+y*chunkSize] = cv;
			}

		for( int y = 0; y < 2; ++y )
			for( int x = 0; x < 2; ++x )
			{
				float lx = x*(chunkSize-1) + cX*(chunkSize-1);
				float ly = y*(chunkSize-1) + cY*(chunkSize-1);
				D3DXVECTOR3 v( lx*12,rWaterLevel_,ly*12 );
				ChunkVertex cv;
				cv.vPos_ = v;
				cv.uv_ = D3DXVECTOR2( x,y);
				water[x+y*2] = cv;
			}

		IDirect3DVertexBuffer9* pVB;
		hr = GraphicEngine::GetDXDevice()->CreateVertexBuffer(sizeof(ChunkVertex)*chunkSize*chunkSize,D3DUSAGE_WRITEONLY,0,D3DPOOL_MANAGED,&pVB,0);
		if( FAILED( hr ) )
			Logger::Log( LOGGING, std::wstring( DXGetErrorString9( hr ) ) + L"CreateVertexBuffer" );
		IDirect3DVertexBuffer9* pVBWater;
		hr = GraphicEngine::GetDXDevice()->CreateVertexBuffer(sizeof(ChunkVertex)*4,D3DUSAGE_WRITEONLY,0,D3DPOOL_MANAGED,&pVBWater,0);
		if( FAILED( hr ) )
			Logger::Log( LOGGING, std::wstring( DXGetErrorString9( hr ) ) + L"CreateVertexBufferWater" );

		if( pVB && pVBWater)
		{
			//printf ("VB ok\n" );
			hr = pVB->Lock(0, 0, &data_ptr,0);
			if( FAILED( hr ) )
				Logger::Log( LOGGING, std::wstring( DXGetErrorString9( hr ) ) + L"Lock height" );
			else
			{
				memcpy( data_ptr, (const void*)&buffer.front(), sizeof(ChunkVertex)*chunkSize*chunkSize);
				pVB->Unlock();
			}
			hr = pVBWater->Lock(0, 0, &data_ptr, 0);
			if( FAILED( hr ) )
				Logger::Log( LOGGING, std::wstring( DXGetErrorString9( hr ) ) + L"Lock water" );
			else
			{
				memcpy( data_ptr, (const void*)&water.front(), sizeof(ChunkVertex)*4);
				pVBWater->Unlock();
			}
			return new Chunk( DXMeshVB( pVB, chunkSize*chunkSize ),DXMeshVB( pVBWater, 4 ), chunkSize, bbox );
			//chunks_.push_back(  );
		}
		return NULL;
	}
	
	void Terran::UpdateWater( float rWaterLevel )
	{
		int nbrChunkX = (sizeX_-1)/(chunkSize-1);
		int nbrChunkY = (sizeY_-1)/(chunkSize-1);
		
		for( int cY = 0; cY < nbrChunkY; ++cY )
		{
			for( int cX = 0; cX < nbrChunkX; ++cX )
			{
			    Chunk* pChunk = chunks_[ cX + cY*nbrChunkX ];
        		HRESULT hr;
        		rWaterLevel_  = rWaterLevel;
        		void* data_ptr;
        		IDirect3DVertexBuffer9* pVB = pChunk->dxWater_.first;
        		hr = pVB->Lock(0, 0, &data_ptr,0);
        		if( FAILED( hr ) )
        			Logger::Log( LOGGING, std::wstring( DXGetErrorString9( hr ) ) + L"Lock water" );
        	    else
        	    {
            		int nbrChunkX = (sizeX_-1)/(chunkSize-1);
            		int nbrChunkY = (sizeY_-1)/(chunkSize-1);
            		for( int y = 0; y < 2; ++y )
            			for( int x = 0; x < 2; ++x )
            			{
                			float lx = x*(chunkSize-1) + cX*(chunkSize-1);
                			float ly = y*(chunkSize-1) + cY*(chunkSize-1);
                			ChunkVertex& cv = ((ChunkVertex*)data_ptr)[x+y*2];
                			D3DXVECTOR3 v( lx*12,rWaterLevel_,ly*12 );
                			cv.vPos_ = v;
                        }
        			pVB->Unlock();
           		}
           	}
        }          
	}
	void Terran::UpdateVB( int left, int top, int right, int bottom, bool bOnlyColor )
	{
		
		left /= (chunkSize-1);
		right /= (chunkSize-1);
		top /= (chunkSize-1);
		bottom /= (chunkSize-1);
		top -= 1;
		bottom += 1;
		right += 1;
		left -= 1;
        		
		int nbrChunkX = (sizeX_-1)/(chunkSize-1);
		int nbrChunkY = (sizeY_-1)/(chunkSize-1);
		
		left = clamp( left, 0, nbrChunkX );
		top = clamp( top, 0, nbrChunkY );
		right = clamp( right, 0, nbrChunkX );
		bottom = clamp( bottom, 0, nbrChunkY );
		//printf("Updating heights %d %d %d %d\n",left,top,right,bottom );
		for( int cY = top; cY < bottom; ++cY )
		{
			for( int cX = left; cX < right; ++cX )
			{
				if( bOnlyColor )
					UpdateColor( cX, cY, chunks_[ cX + cY*nbrChunkX ] );
				else
					UpdateHeight( cX, cY, chunks_[ cX + cY*nbrChunkX ] );
				/*{
					delete chunks_[ cX + cY*nbrChunkX ];
					chunks_[ cX + cY*nbrChunkX ] = 0;
					Chunk* pTemp = CreateOne( cX, cY );
					if( pTemp )
						chunks_[ cX + cY*nbrChunkX ] = pTemp;
					else
						printf("Error creating a VB\n" );
				}*/
			}
		}
	}
	void Terran::UpdateHeight( float* pHeight, float waterLevel, int left, int top, int right, int bottom )
	{
		rWaterLevel_ = waterLevel;
		memcpy( pHeight_, pHeight, sizeX_*sizeY_*sizeof(float) );
		//printf("Chunk nbr = %d %d", nbrChunkX, nbrChunkY );
		UpdateVB( left,top,right,bottom, false);
	}

	void Terran::UpdateRGB( unsigned char* rgb )
	{
		memcpy( rgb_, rgb, sizeX_*sizeY_*3 );
		UpdateVB( 0,0,sizeX_,sizeY_, true );
	}

	float Terran::HeightInWorld( const D3DXVECTOR3& v ) const
	{
		D3DXVECTOR3 v0 = v/12.f;
		v0.x = (float)(int)v0.x;
		v0.z = (float)(int)v0.z;
		if( v0.x < 0 )
			return v.y;
		if( v0.z < 0 )
			return v.y;
		if( v0.x >= sizeX_-1 )
			return v.y;
		if( v0.z >= sizeY_-1 )
			return v.y;
		D3DXVECTOR3 v1 = v0 + D3DXVECTOR3( 1, 0, 0 ) ;
		D3DXVECTOR3 v2 = v0 + D3DXVECTOR3( 0, 0, 1 ) ;
		D3DXVECTOR3 v3 = v0 + D3DXVECTOR3( 1, 0, 1 ) ;
		float rAlphaX = ((int)v.x%12)/12.f;
		float rAlphaY = ((int)v.z%12)/12.f;

		float rHeight0 = pHeight_[ (int)v0.x + (int)v0.z * sizeX_ ];
		float rHeight1 = pHeight_[ (int)v1.x + (int)v1.z * sizeX_ ];
		float rHeight2 = pHeight_[ (int)v2.x + (int)v2.z * sizeX_ ];
		float rHeight3 = pHeight_[ (int)v3.x + (int)v3.z * sizeX_ ];

		float rHeight01 = rHeight0 * ( 1.f - rAlphaX ) + rHeight1 * rAlphaX;
		float rHeight23 = rHeight2 * ( 1.f - rAlphaX ) + rHeight3 * rAlphaX;
		float rHeight = rHeight01 * ( 1.f - rAlphaY ) + rHeight23 * rAlphaY;
		return rHeight;
	}

	D3DXVECTOR3 Terran::Intersect( const D3DXVECTOR3& vFrom, const D3DXVECTOR3& vDir )const
	{
		D3DXVECTOR3 vCur = vFrom;
		while( 1 )
		{
			vCur += vDir*12;
			float h = HeightInWorld( vCur );
			if( h > 6000 && vFrom.y < 6000 )
				break;
			if( h < 0 )
				break;
			if( vCur.y < h )
				break;
		}
		if( vCur.x < 0 )
			vCur.x = 0;
		if( vCur.z < 0 )
			vCur.z = 0;
		if( vCur.x >= sizeX_*12.f )
			vCur.x = (sizeX_-1)*12.f;
		if( vCur.z >= sizeY_*12.f )
			vCur.z = (sizeY_-1)*12.f;
		vCur.y = HeightInWorld( vCur );
		return vCur;
	}

	void Terran::Draw( bool bRenderWater )
	{
		std::vector< Chunk* >::iterator it =  chunks_.begin();
		std::vector< Chunk* >::iterator itEnd =  chunks_.end();
		int nD = 0;
		while( it != itEnd )
		{
			//if (nD != 31)
				(*it)->Render( pIB_, pvtxDecl_ );
			++it;
			++nD;
//			if (nD == 26)
//				break;
		}
		if( bRenderWater )
		{
			it =  chunks_.begin();		
			while( it != itEnd )
			{
				(*it)->RenderWater( pvtxDecl_ );
				++it;
			}
		}
	};

	FrontEndCreator* g_pFC=0;
	bool InitD3D( HWND hWnd )
	{
		g_pFC = new FrontEndCreator( hWnd, true );
		return true;
	}
	void CloseD3D()
	{
		if( g_pFC )
			delete g_pFC;
		g_pFC = 0;

	}
	void CloseTerran( )
	{
		delete g_pMouse;
		delete g_pTerran;
	}
	void UpdateTerran( float* height,float waterLevel,int left, int top, int right, int bottom )
	{
		if( g_pTerran)
			g_pTerran->UpdateHeight( height, waterLevel,left,top,right,bottom );
	}
	void UpdateRGB( unsigned char* rgb )
	{
		if( g_pTerran)
			g_pTerran->UpdateRGB( rgb );
	}

	void UpdateWater( float water )
	{
		if( g_pTerran)
			g_pTerran->UpdateWater( water );
	}

	void SaveToFile( const std::wstring& strFileName )
	{
		IDirect3DSurface9 * pRT;
		HRESULT hr = GetDXDevice()->GetRenderTarget( 0, &pRT );
		if( FAILED( hr ) )
		{
			Logger::Log( LOGGING, std::wstring( DXGetErrorString9( hr ) ) + L"GetRT" );
			return;
		}
		if( strFileName.find( L".jpg" ) !=std::wstring::npos )
			hr =D3DXSaveSurfaceToFile( strFileName.c_str(), D3DXIFF_JPG, pRT,0,0);
		else if( strFileName.find( L".bmp" ) !=std::wstring::npos)
			hr =D3DXSaveSurfaceToFile( strFileName.c_str(), D3DXIFF_BMP, pRT,0,0);
		else if( strFileName.find( L".png" ) !=std::wstring::npos)
			hr =D3DXSaveSurfaceToFile( strFileName.c_str(), D3DXIFF_PNG, pRT,0,0);
		if( FAILED( hr ) )
		{
			Logger::Log( LOGGING, std::wstring( DXGetErrorString9( hr ) ) + L"SaveToFile" );
		}
		pRT->Release();
	}
	void InitTerran( float rWaterLevel, int xSize, int ySize, float* height, unsigned char* rgb )
	{
		bool bAlreadyInit = false;

		if( g_pTerran )
		{ 
			bAlreadyInit = true;
			delete g_pTerran;
		}
		g_pTerran=new Terran( rWaterLevel, xSize, ySize, height, rgb );
		if( !bAlreadyInit )
		{
			g_pMouse = new MouseRep();
			D3DXVECTOR3 vEyePt( 64*12,max( g_pTerran->GetHeight( 0,0 ),g_pTerran->GetHeight( 64,64 ))+1000,64*12 );
			D3DXVECTOR3 vLookatPt( 0,g_pTerran->GetHeight( 0,0 ),0 );
			D3DXMATRIXA16 matIdent;
			D3DXMatrixIdentity( &matIdent );
			FrontEnd::Ref().SetWorldTransform( matIdent );
			D3DXMATRIXA16 matProj;
			D3DXMatrixPerspectiveFovRH( &matProj, D3DX_PI/4, 1.0f, 12.0f, 2048.0f*12 );
			FrontEnd::Ref().SetProjTransform( matProj );


			g_Camera.SetAt( vLookatPt );
			g_Camera.SetPos( vEyePt );
			g_Camera.Render();
		}


	}
	void Update( int mx, int my, bool bRenderWater )
	{
		static bool bFirst = true;
		FrontEnd::Ref().Clear( D3DCLEAR_TARGET|D3DCLEAR_ZBUFFER, g_bgcolor, 1.f, 0.f );
		FrontEnd::Ref().BeginScene();
		g_Camera.Render();
		if( g_pTerran )
			g_pTerran->Draw( bRenderWater );
		if( g_pMouse && !bFirst )
			g_pMouse->Render( mx,my );
		bFirst =false;
		FrontEnd::Ref().EndScene();
		FrontEnd::Ref().Present();
	}
	void SetbgColor( int r, int g, int b)
	{
		g_bgcolor = D3DCOLOR_RGBA( r,g,b,255 );
	}
	D3DXVECTOR2 GetCoordUnderMouse( int mx, int my)
	{
		return g_pMouse->GetVertexMouse( mx, my );
	}
	D3DXVECTOR2 GetFloatCoordUnderMouse( int mx, int my)
	{
		return g_pMouse->GetFloatVertexMouse( mx, my );
	}
	void MoveCam( int x, int y )
	{
		D3DXVECTOR3 vAt = g_Camera.GetAt();
		D3DXVECTOR3 vPos = g_Camera.GetPos();
		D3DXVECTOR3 vOffset = vAt - vPos;
		g_Camera.SetAt( D3DXVECTOR3( x*12, g_pTerran->GetHeight( x,y ), y*12 ) ) ;
		g_Camera.SetPos( D3DXVECTOR3( x*12, g_pTerran->GetHeight( x,y ), y*12 ) - vOffset );
	}
}

extern "C"
{
static PyObject *DX_Init( PyObject *self, PyObject *args )
{
	int hwnd ;
	if (!PyArg_ParseTuple(args, "i", &hwnd))
        return NULL;
	GraphicEngine::InitD3D( (HWND)hwnd );
	if( GraphicEngine::FrontEnd::IsValid() )
	{
	    printf("valid");
	    return Py_BuildValue( "i", 1 );
	}
	printf("invalid");
	return Py_BuildValue( "i", 0 );
}

static PyObject *DX_Close( PyObject *self, PyObject *args )
{
	GraphicEngine::CloseD3D(  );
	Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *DX_CloseTerran( PyObject *self, PyObject *args )
{
	GraphicEngine::CloseTerran(  );
	Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *DX_Update( PyObject *self, PyObject *args )
{
	int mx,my,renderWater;

	if (!PyArg_ParseTuple(args, "iii", &mx,&my,&renderWater))
        return NULL;
	GraphicEngine::Update( mx,my, renderWater);
	Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *DX_InitTerran( PyObject *self, PyObject *args )
{
	char* buffer;
	int len;
	int xSize, ySize;
	float rWaterLevel;
	unsigned char* rgb;
	int lenRGB;
	if (!PyArg_ParseTuple(args, "f(ii)s#s#", &rWaterLevel, &ySize,&xSize,&buffer, &len,&rgb,&lenRGB))
        return NULL;
	GraphicEngine::InitTerran( rWaterLevel, xSize, ySize, (float*)buffer,rgb );
	Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *DX_UpdateColors( PyObject *self, PyObject *args )
{
	char* buffer;
	int len;
	if (!PyArg_ParseTuple(args, "s#", &buffer, &len))
        return NULL;
	GraphicEngine::UpdateRGB( (unsigned char*)buffer );
	Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *DX_UpdateTerran( PyObject *self, PyObject *args )
{
	char* buffer;
	int len;
	float waterLevel;
	int left, top, right, bottom;
	if (!PyArg_ParseTuple(args, "s#f(iiii)", &buffer, &len,&waterLevel,&left,&top,&right,&bottom))
        return NULL;
	GraphicEngine::UpdateTerran( (float*)buffer,waterLevel,left,top,right,bottom );
	Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *DX_UpdateWater( PyObject *self, PyObject *args )
{
	float waterLevel;
	if (!PyArg_ParseTuple(args, "f", &waterLevel))
        return NULL;
	GraphicEngine::UpdateWater( waterLevel );
	Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *DX_Strafe( PyObject *self, PyObject *args )
{
	float amount;
	if (!PyArg_ParseTuple(args, "f", &amount))
        return NULL;
	GraphicEngine::g_Camera.Strafe(amount);
	Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *DX_Move( PyObject *self, PyObject *args )
{
	float amount;
	if (!PyArg_ParseTuple(args, "f", &amount))
        return NULL;
	GraphicEngine::g_Camera.Move(amount);
	Py_INCREF(Py_None);
    return Py_None;
}


static PyObject *DX_RotX( PyObject *self, PyObject *args )
{
	float amount;
	if (!PyArg_ParseTuple(args, "f", &amount))
        return NULL;
	GraphicEngine::g_Camera.RotX(amount);
	Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *DX_RotY( PyObject *self, PyObject *args )
{
	float amount;
	if (!PyArg_ParseTuple(args, "f", &amount))
        return NULL;
	GraphicEngine::g_Camera.RotY(amount);
	Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *DX_MoveUp( PyObject *self, PyObject *args )
{
	float amount;
	if (!PyArg_ParseTuple(args, "f", &amount))
        return NULL;
	GraphicEngine::g_Camera.MoveUp(amount);
	Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *DX_TurnGrid( PyObject *self, PyObject *args )
{
	GraphicEngine::g_bWired = !GraphicEngine::g_bWired;
	Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* DX_GetDoc( PyObject *self, PyObject *args )
{
	TCHAR szPath[MAX_PATH];
	SHGetFolderPath( 0, 0x5, 0,SHGFP_TYPE_CURRENT,szPath );
	PyObject* pRet;
	pRet = Py_BuildValue( "u", szPath );
	return pRet;
}

static PyObject* DX_GetCoordUnderMouse( PyObject *self, PyObject *args )
{
	int mx,my;
	if (!PyArg_ParseTuple(args, "ii", &mx,&my))
        return NULL;
	D3DXVECTOR2 v = GraphicEngine::GetCoordUnderMouse( mx,my );
	PyObject* pRet;
	pRet = Py_BuildValue( "ii", (int)v.x,(int)v.y );
	return pRet;
}

static PyObject* DX_GetFloatCoordUnderMouse( PyObject *self, PyObject *args )
{
	int mx,my;
	if (!PyArg_ParseTuple(args, "ii", &mx,&my))
        return NULL;
	D3DXVECTOR2 v = GraphicEngine::GetFloatCoordUnderMouse( mx,my );
	PyObject* pRet;
	pRet = Py_BuildValue( "ff", v.x,v.y );
	return pRet;
}

static PyObject* DX_SetBg( PyObject *self, PyObject *args )
{
	int r,g,b;
	if (!PyArg_ParseTuple(args, "(iii)", &r,&g,&b))
        return NULL;
	GraphicEngine::SetbgColor( r,g,b );
	Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* DX_MouseShape( PyObject *self, PyObject *args )
{
	int radius, shape;
	if (!PyArg_ParseTuple(args, "ii", &radius,&shape))
        return NULL;
    if( GraphicEngine::g_pMouse )
    {
    GraphicEngine::g_pMouse->SetRadius( radius );
    GraphicEngine::g_pMouse->SetShape( shape );
    }
	Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* DX_SaveToFile( PyObject *self, PyObject *args )
{
	LPCWSTR szFileName;
	if (!PyArg_ParseTuple(args, "u", &szFileName))
        return NULL;
	GraphicEngine::SaveToFile( szFileName );
	Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* DX_MoveCam( PyObject *self, PyObject *args )
{
	int x, y;
	if (!PyArg_ParseTuple(args, "(ii)", &x,&y))
        return NULL;
	GraphicEngine::MoveCam( x,y );
	Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* DX_GetVersion( PyObject *self, PyObject *args )
{
	PyObject* pRet;
	pRet = Py_BuildValue( "s", "v1.0c" );
	return pRet;
}

static PyMethodDef dxEngineMethods[] =
{
	{"init", DX_Init, METH_VARARGS, "init" },
	{"setBgColor", DX_SetBg, METH_VARARGS, "setBgColor" },
	{"close", DX_Close, METH_VARARGS, "close" },
	{"update", DX_Update, METH_VARARGS, "update" },
	{"initTerran", DX_InitTerran, METH_VARARGS, "initTerran" },
	{"updateTerran", DX_UpdateTerran, METH_VARARGS, "updateTerran" },
	{"updateWater", DX_UpdateWater, METH_VARARGS, "updateWater" },
	{"updateColors", DX_UpdateColors, METH_VARARGS, "updateColors" },
	{"closeTerran", DX_CloseTerran, METH_VARARGS, "closeTerran" },
	{"strafe", DX_Strafe, METH_VARARGS, "strafe camera" },
	{"move", DX_Move, METH_VARARGS, "move camera" },
	{"rotX", DX_RotX, METH_VARARGS, "rotate camera pitch" },
	{"rotY", DX_RotY, METH_VARARGS, "rotate camera yaw" },
	{"moveUp", DX_MoveUp, METH_VARARGS, "move camera up/down" },
	{"turnGrid", DX_TurnGrid, METH_VARARGS, "turn grid on/off" },
	{"GetDoc", DX_GetDoc, METH_VARARGS, "return user docfolder" },
	{"getCoordUnderMouse", DX_GetCoordUnderMouse, METH_VARARGS,"get the grid pixel under mouse" },
	{"getFloatCoordUnderMouse", DX_GetFloatCoordUnderMouse, METH_VARARGS,"get the pixel ( float number ) under mouse" },
	{"mouseShape", DX_MouseShape, METH_VARARGS,"set mouse shape" },
	{"saveToFile", DX_SaveToFile, METH_VARARGS,"save image to file" },
	{"moveCamera", DX_MoveCam,METH_VARARGS,"move camera" },
	{"GetVersion", DX_GetVersion,METH_VARARGS,"get dll version" },
    {NULL, NULL, 0, NULL}        /* Sentinel */
};


_declspec( dllexport ) void  initdxEngine(void)
{
    (void) Py_InitModule("dxEngine", dxEngineMethods);
}
}
