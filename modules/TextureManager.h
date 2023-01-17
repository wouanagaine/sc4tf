#ifndef TextureManager_included
#define TextureManager_included

#include <string>

struct IDirect3DBaseTexture9;
namespace GraphicEngine
{

	
	class Texture;
	struct TextureManagerImpl;

	IDirect3DBaseTexture9* ToDX( const Texture& tex ) ;

	class TextureManager
	{
		TextureManager( const TextureManager& );
		TextureManager& operator=( const TextureManager& );

	public:

		explicit TextureManager();
		~TextureManager();

		Texture* GetTexture( const std::wstring& strTexName );
		void FreeAllTextures();
	private:
		TextureManagerImpl* pImpl_;
	};
}
#endif