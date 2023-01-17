////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////
#include <python.h>
#include <malloc.h>
#include <memory.h>
#include <math.h>
#include <vector>
#include <map>
#include <dx/d3dx9.h>

inline 
float Lerp( float a, float b, float alpha )
{
    return (1.f-alpha)*a+b*alpha;
}

float Dot( float* v1, float* v2 )
{
    return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2];
}


class Spline
{
public:
	Spline() : controls_(), tangents_(), offsets_() {}

	void AddControl( const D3DXVECTOR2& cp )
	{
		controls_.push_back( cp.y );
		offsets_.push_back(cp.x);
	}
	void Init();

	float operator[]( float r );
private:
	std::vector< float > controls_;
	std::vector< float > tangents_;
	std::vector< float > offsets_;
	float rTotalLen_;
};

void Spline::Init()
{
	int n = controls_.size();
	tangents_.clear();
	tangents_.resize( controls_.size() );
	tangents_.front() = (0.5f) *( controls_[1] - controls_[0] );
	tangents_.back() = (0.5f) *( controls_.back() - controls_[n-2] );

	rTotalLen_ = 0.f;
	for( int i = 1; i < n - 1; ++i )
		tangents_[i] = (0.5f) *( controls_[i+1] - controls_[i-1] );


}


float Spline::operator[]( float r )
{
	float t = 0.f;
	if( r >= 1.f )
	{
		t = offsets_.size() - 1.f;
	}
	else if( r <= 0.f )
	{
		t = 0.f;
	}
	else for( int i = 0; i < offsets_.size() - 1; ++i )
	{
		if( offsets_[ i + 1 ] >= r )
		{
			t = i + ( r - offsets_[i] ) /( offsets_[ i + 1 ] - offsets_[ i ] );
			break;
		}
	}

	int nCurIdx  = static_cast<int>( t ), 
		nNextIdx = static_cast<int>( min( nCurIdx + 1, offsets_.size()  - 1 ) );

    t = static_cast<float>( fmod( t, 1.0f ) );

	float t_2 = t * t,
          t_3 = t_2 * t;

    float t3_2 = 2 * t_3; 
    float t2_3 = 3 * t_2; 

	return ( ( controls_ [ nCurIdx  ] * static_cast<float>( t3_2 - t2_3 + 1.0f  ) ) +	// Weighed "from" control point
			 ( controls_ [ nNextIdx ] * static_cast<float>(-t3_2 + t2_3         ) ) +	// Weighed "to"   control point
			 ( tangents_ [ nCurIdx  ] * static_cast<float>( t_3  - 2 * t_2 + t  ) ) +	// Weighed "from" tangent
			 ( tangents_ [ nNextIdx ] * static_cast<float>( t_3  -     t_2      ) ) );	// Weighed "to"   tangent
}

void TestSpline()
{
	Spline shape;
	shape.AddControl( D3DXVECTOR2(0,1) );
	shape.AddControl( D3DXVECTOR2(0.7,1) );
	shape.AddControl( D3DXVECTOR2(.8,1.8) );
	shape.AddControl( D3DXVECTOR2(.95,0) );
	shape.AddControl( D3DXVECTOR2(1,0) );
	shape.Init();
	float v = shape[0.f];
	v = shape[.35];
	v = shape[.5];
	v = shape[.7];
	v = shape[.81];
	v = shape[1.f];
}

unsigned char* expand( int xSize, int ySize, unsigned char* height )
{
	unsigned char* newheights = (unsigned char*)malloc( xSize*ySize);
	unsigned char* pCur = height;
	unsigned char* pWrite = newheights;

	memcpy( newheights, height, xSize*ySize );
	for( int y = 0; y< ySize; ++y )
		for( int x = 0; x< xSize; ++x, ++pCur, ++pWrite )
		{
			unsigned char h = *pCur;
			if( h != 0 )
			{
				for( int j = -1; j< 2; ++j )
					for( int i= -1; i< 2; ++i )
					{
						if( x+i<0)
							continue;
						if( x+i>=xSize)
							continue;
						if( y+j<0)
							continue;
						if( y+j>=ySize)
							continue;
						int lx = x+i;
						int ly = y+j;
						if( height[lx+ly*xSize ] == 0 )
							newheights[lx+ly*xSize ] = h;
					}
			}	
		}
	return newheights;
}
inline
void ComputeNormal( float* norm, int x, int y, int xSize, int ySize, float* height)
{
	memset( norm, 0, sizeof( float )*3 );
	if( x == 0 || x == xSize-1 || y == 0 || y == ySize -1 )
		return;
	float* pCurr = &height[x+y*xSize ];
	float dx = *(pCurr-1)- *(pCurr+1);
	float dy = *(pCurr-xSize)- *(pCurr+xSize);
	float dz = 2.f;
	float mag = (float)sqrt( dx*dx + dy*dy +dz*dz );
	norm[0] = dx/mag;
	norm[1] = dz/mag;
	norm[2] = dy/mag;
}

float* GenerateNormal( int xSize, int ySize, float* height )
{
	int y,x;
	float dx,dy,dz,mag;
	float* norms;
	float* pCurr;
	norms = (float*)malloc( xSize*ySize*3*sizeof(float) );
	pCurr = norms+xSize*3;
	for( y = 1; y < ySize -1; ++y )
	{
		pCurr+=3;
		for( x = 1; x < xSize -1; ++x )
		{
            dx = height[x-1 + y * xSize]- height[x+1 + y*xSize];
            dy = height[x+(y-1)*xSize]- height[x+(y+1)*xSize];
            dz = 2.f;
			mag = (float)sqrt( dx*dx + dy*dy +dz*dz );
			*(pCurr++) = dx/mag;
			*(pCurr++) = dz/mag;
			*(pCurr++) = dy/mag;
		}
		pCurr+=3;
	}
	return norms;
}


void GenerateShadow( bool bLight, int yStart, int yMax, int xSize, int ySize, float* lightDir, float* height, float* norms, unsigned char* shadow )
{
	int y,x;
//	unsigned char* shadow;
	float vertex[3];
	float h,l,v;
	//lightDir[0] =1;
	//lightDir[2] =-1;
//	shadow = (unsigned char*)malloc( xSize*ySize );
//	memset( shadow, 0xFF, xSize*ySize );
	if( yMax > ySize )
		yMax = ySize;
	for( y = yStart; y < yMax; ++y )
		for( x = 0; x < xSize; ++x )
		{
			if( shadow[ x + y*xSize ] == 127)
				continue;
			h = height[ x+y*xSize]/7.f;
			vertex[0] = x;
			vertex[1] = h;
			vertex[2] = y;
			float norm[3];
			ComputeNormal( norm, x, y, xSize, ySize, height );
			//l = Dot( &norms[(x+y*xSize)*3], lightDir );
			l = Dot( norm, lightDir );
			if( l < 0 )
			{
				v = (l) * 64.f;
				shadow[ x+y*xSize ] = 191-(int)v;
			}
			while( bLight )
			{
                vertex[0] += 1;
                vertex[1] += lightDir[1];
                vertex[2] += -1;
                if( vertex[1] < 0 )
                    break;
                if( vertex[0] < 0 )
					break;
                if( vertex[2] < 0 )
                    break;
                if( vertex[0] >= xSize )
                    break;
                if( vertex[2] >= ySize )
                    break;
				/*if( shadow[ (int)vertex[0]+ (int) vertex[2] * xSize ] == 127 )
					break;*/

                h = height[ (int) vertex[0] + (int)vertex[2] * xSize ]/7.f;
                    
                if( h < vertex[1] )
                    shadow[ (int)vertex[0]+ (int) vertex[2] * xSize ] = 127;
			}
				
		}
/*	unsigned char* newShadow = (unsigned char*)malloc( xSize*ySize );
	for( y = 0; y < ySize ; ++y )
	{
		for( x = 0; x < xSize; ++x )
		{
			float rVal = 0.f;
			float nbr=0.f;
			for( int j = -1; j< 2; ++j )
				for( int i= -1; i< 2; ++i )
				{
					if( x+i<0)
						continue;
					if( x+i>=xSize)
						continue;
					if( y+j<0)
						continue;
					if( y+j>=ySize)
						continue;
					int lx = x+i;
					int ly = y+j;
					rVal += shadow[ lx + ly * xSize ];
					nbr += 1.f;
				}
			newShadow[ x+y*xSize ] = (unsigned char)(rVal/nbr);
		}
	}
	memcpy( shadow, newShadow, xSize*ySize );
	free( newShadow );*/
//	return shadow;
}

struct RGBColor
{
    RGBColor( int _r, int _g, int _b ):r(_r),g(_g),b(_b) {}
    
    int r,g,b;
};


struct Gradient
{
    explicit Gradient( PyObject* p )
    : colors_()
    {
    	if( PyDict_Check( p ) )
    	{
    		PyObject *key, *value;
    		int pos = 0;
    
    		while (PyDict_Next(p, &pos, &key, &value)) 
    		{
    			int k;
    			int r,g,b;
    			if( PyInt_Check( key ) )
    			{
    				k = PyInt_AsLong( key );
    				//printf("key ok %d\n",k );
    			}
    			else
    			{
    				printf("key not ok\n" );
    			}
    			if( PyTuple_Check( value ) )
    			{
    			    r = PyInt_AsLong( PyTuple_GetItem( value,0 ) );
    			    g = PyInt_AsLong( PyTuple_GetItem( value,1 ) );
    			    b = PyInt_AsLong( PyTuple_GetItem( value,2 ) );
    			    //printf("value ok %d\n",r,g,b );
    			    colors_.insert( std::make_pair( k, RGBColor( r,g,b) ) );
    			}
    			else
    				printf("value not ok\n" );
            }        
        }        
        printf("----\n" );
    }

    RGBColor GetColor( int value ) const
    {
        std::map<int, RGBColor >::const_iterator it = colors_.begin();
        std::map<int, RGBColor >::const_iterator itEnd = colors_.end();
        if( value < it->first )
        {
//			printf("value under %d, %d\n",value,it->first );

            return it->second;
        }
        std::map<int, RGBColor >::const_iterator justInCase = it;
        while( it != itEnd )
        {
            if( value < it->first )
            {
                float distTot = it->first - justInCase->first;
                float distCur = value-justInCase->first;
                float alpha = distCur/distTot;
                float r = Lerp( justInCase->second.r, it->second.r, alpha );
                float g = Lerp( justInCase->second.g, it->second.g, alpha );
                float b = Lerp( justInCase->second.b, it->second.b, alpha );
                return RGBColor( r,g,b );
            }
            justInCase = it;
            
            ++it;
        }        
//		printf("value above %d, %d\n",value,justInCase->first );
        return justInCase->second;            
    }
    
    std::map<int, RGBColor > colors_;    
};

unsigned char* OnePassColors( bool bLight, int xSize, int ySize, float waterLevel, float* height, const Gradient& waterGrad, const Gradient& landGrad, float* lightDir )
{
	int x,y;
	unsigned char* colors;
	colors = (unsigned char*)malloc( xSize*ySize*3 );
	memset( colors, 0xFF, xSize*ySize*3 );
	float vertex[3];
	float h,l,v;
	float* pCurrHeight = height;
	unsigned char* pCurrColor = colors;
	for( y = 0; y < ySize; ++y )
	{
		for( x = 0; x < xSize; ++x, ++pCurrHeight )
		{
			float h = *pCurrHeight;
			if( !(*pCurrColor == 255 && *(pCurrColor+1) == 255 && *(pCurrColor+2) == 255 ) )
			{
				pCurrColor+=3;
				continue;
			}
			float norm[3];
			ComputeNormal( norm, x, y, xSize, ySize, height );
			float n = norm[1]*255.f;


			unsigned char c = 0xFF;
			l = Dot( norm, lightDir );
			if( l < 0 )
			{
				v = (l) * 64.f;
				c = 191-(int)v;
			}							
			if( n < 20 )
			{
				*(pCurrColor++) = c/2;
				*(pCurrColor++) = c/2;
				*(pCurrColor++) = c/2;
			}
			else if( h < waterLevel )
			{
				float v = waterLevel - h;
                RGBColor col = waterGrad.GetColor( v );
				
				int r = col.r * c;
				int g = col.g * c;
				int b = col.b * c;
				r >>= 8;
				g >>= 8;
				b >>=8;				
				*(pCurrColor++) = r;
				*(pCurrColor++) = g;
				*(pCurrColor++) = b;
			}
			else
			{
				
				float v = h  - waterLevel;
                RGBColor col = landGrad.GetColor( v );
                
				int r = col.r * c;
				int g = col.g * c;
				int b = col.b * c;
				r >>= 8;
				g >>= 8;
				b >>=8;				
				*(pCurrColor++) = r;
				*(pCurrColor++) = g;
				*(pCurrColor++) = b;
			}
			// propagate shadows
			vertex[0] = x;
			vertex[1] = h/7.f;
			vertex[2] = y;
			while( bLight )
			{
                vertex[0] += 1;
                vertex[1] += lightDir[1];
                vertex[2] += -1;
                if( vertex[1] < 0 )
                    break;
                if( vertex[0] < 0 )
					break;
                if( vertex[2] < 0 )
                    break;
                if( vertex[0] >= xSize )
                    break;
                if( vertex[2] >= ySize )
                    break;

                h = height[ (int) vertex[0] + (int)vertex[2] * xSize ];
                    
                if( h/7.f < vertex[1] )
				{
					int lx = (int)vertex[0];
					int ly = (int)vertex[2];
					c=127;
					ComputeNormal( norm, lx, ly, xSize, ySize, height );
					float n = norm[1]*255.f;
					unsigned char* pOld = pCurrColor;
					pCurrColor = &colors[ (lx + ly*xSize)*3 ];

					if( n < 20 )
					{
						*(pCurrColor++) = c/2;
						*(pCurrColor++) = c/2;
						*(pCurrColor++) = c/2;
					}
					else if( h < waterLevel )
					{
						float v = waterLevel - h;
						RGBColor col = waterGrad.GetColor( v );
						
						int r = col.r * c;
						int g = col.g * c;
						int b = col.b * c;
						r >>= 8;
						g >>= 8;
						b >>=8;				
						*(pCurrColor++) = r;
						*(pCurrColor++) = g;
						*(pCurrColor++) = b;
					}
					else
					{
						
						float v = h  - waterLevel;
						RGBColor col = landGrad.GetColor( v );
		                
						int r = col.r * c;
						int g = col.g * c;
						int b = col.b * c;
						r >>= 8;
						g >>= 8;
						b >>=8;				
						*(pCurrColor++) = r;
						*(pCurrColor++) = g;
						*(pCurrColor++) = b;
					}
					pCurrColor = pOld;
				}
			}
		}
	}
//	printf("Colorsfinished\n");
	return colors;
}

unsigned char* GenerateColors( int xSize, int ySize, float waterLevel, float* height, float* norms, unsigned char* shadows, const Gradient& waterGrad, const Gradient& landGrad )
{
	int x,y;
	unsigned char* colors;
	colors = (unsigned char*)malloc( xSize*ySize*3 );
	memset( colors, 0xFF, xSize*ySize*3 );
	for( y = 0; y < ySize; ++y )
	{
		for( x = 0; x < xSize; ++x )
		{
			float h = height[ x + y * xSize ];
			float norm[3];
			ComputeNormal( norm, x, y, xSize, ySize, height );
			float n = norm[1]*255.f;
			//float n = norm[ (x+y*xSize)*3+1 ]*255.f;
            if( n < 20 )
			{
				unsigned char c = shadows[ (x+y*xSize) ];
				colors[ (x+y*xSize)*3+0 ] = c/2;
				colors[ (x+y*xSize)*3+1 ] = c/2;
				colors[ (x+y*xSize)*3+2 ] = c/2;
			}
			else if( h < waterLevel )
			{
			    
				unsigned char c = shadows[ (x+y*xSize) ];
				
				float v = waterLevel - h;
                RGBColor col = waterGrad.GetColor( v );
				
				int r = col.r * c;
				int g = col.g * c;
				int b = col.b * c;
				r >>= 8;
				g >>= 8;
				b >>=8;				
				colors[ (x+y*xSize)*3+0 ] = r;
				colors[ (x+y*xSize)*3+1 ] = g;
				colors[ (x+y*xSize)*3+2 ] = b;
			}
			else
			{
				unsigned char c = shadows[ (x+y*xSize) ];
				
				float v = h  - waterLevel;
                RGBColor col = landGrad.GetColor( v );
                
				int r = col.r * c;
				int g = col.g * c;
				int b = col.b * c;
				r >>= 8;
				g >>= 8;
				b >>=8;				
				colors[ (x+y*xSize)*3+0 ] = r;
				colors[ (x+y*xSize)*3+1 ] = g;
				colors[ (x+y*xSize)*3+2 ] = b;
			}
		}
	}
//	printf("Colorsfinished\n");
	return colors;
}

float* Egalize( int xSize, int ySize, float* height )
{
	
	int y,x;
	float* newheight;
	float filter[9];
	int lx, ly;
	int i,j;
//	for( i = 0; i< 9; ++i)
//		filter[i] = 1.f;
	newheight = (float*)malloc( xSize*ySize*sizeof(float) );
	for( y = 0; y < ySize ; ++y )
	{
		for( x = 0; x < xSize; ++x )
		{
			float rVal = 0.f;
			float nbr=0.f;
			for( j = -1; j< 2; ++j )
				for( i= -1; i< 2; ++i )
				{
					if( x+i<0)
						continue;
					if( x+i>=xSize)
						continue;
					if( y+j<0)
						continue;
					if( y+j>=ySize)
						continue;
					lx = x+i;
					ly = y+j;
					rVal += height[ lx + ly * xSize ];
					nbr += 1.f;
				}
			newheight[ x+y*xSize ] = rVal/nbr;
		}
	}
//	printf( "egalizefinish\n");
	return newheight;
}
float* WeatherErosion( int xSize, int ySize, float* height, float T, float pct, int nbIter )
{
	int y,x;
	float* newheight;
	
	int lx, ly;
	int i,j;
	
	float actualH, deltaH,addedDiff,rubble;
	newheight = (float*)malloc( xSize*ySize*sizeof(float) );
	memcpy( newheight, height, xSize*ySize*sizeof(float) );
    	
    while( nbIter-- )
    {
    	for( y = 0; y < ySize ; ++y )
    	{
    		for( x = 0; x < xSize; ++x )
    		{
    		    
    			actualH = height[ x+y*xSize ];
    			addedDiff =0.;
				float maxH = 0;
				float sumLower = 0;
    			for( j = -1; j< 2; ++j )
    				for( i= -1; i< 2; ++i )
    				{
    				    if( i == 0 && j == 0 )
    				        continue;
    					if( x+i<0)
    						continue;
    					if( x+i>=xSize)
    						continue;
    					if( y+j<0)
    						continue;
    					if( y+j>=ySize)
    						continue;
    					lx = x+i;
    					ly = y+j;
    					deltaH = actualH - height[ lx + ly * xSize ];
						if( deltaH > maxH )
							maxH = deltaH;
						if( deltaH > 0 )
							sumLower += deltaH;

					}
    			for( j = -1; j< 2; ++j )
    				for( i= -1; i< 2; ++i )
    				{
    				    if( i == 0 && j == 0 )
    				        continue;
    					if( x+i<0)
    						continue;
    					if( x+i>=xSize)
    						continue;
    					if( y+j<0)
    						continue;
    					if( y+j>=ySize)
    						continue;
    					lx = x+i;
    					ly = y+j;
    					deltaH = actualH - height[ lx + ly * xSize ];
    					if( deltaH > T )
    					{
    					    
        				    rubble = pct * (deltaH/sumLower);
        				    newheight[ lx + ly * xSize ] = height[ lx + ly *xSize]+rubble;
                            addedDiff += rubble;                    					    
    				    }
    				    //else
//    				        newheight[ lx + ly * xSize ] = height[ lx + ly *xSize];
//    				    printf("\n");
    				}
    			newheight[ x+y*xSize ] -= addedDiff;
    		}
    	}
    	memcpy( height, newheight, xSize*ySize*sizeof(float) );
	}
	return newheight;

}/*
float* WeatherErosion( int xSize, int ySize, float* height, float T, float pct, int nbIter )
{
	int y,x;
	float* newheight;
	
	int lx, ly;
	int i,j;
	
	float actualH, deltaH,addedDiff,rubble;
	newheight = (float*)malloc( xSize*ySize*sizeof(float) );
	memcpy( newheight, height, xSize*ySize*sizeof(float) );
    	
    while( nbIter-- )
    {
    	for( y = 0; y < ySize ; ++y )
    	{
    		for( x = 0; x < xSize; ++x )
    		{
    		    
    			actualH = height[ x+y*xSize ];
    			addedDiff =0.;
    			for( j = -1; j< 2; ++j )
    				for( i= -1; i< 2; ++i )
    				{
    				    if( i == 0 && j == 0 )
    				        continue;
    					if( x+i<0)
    						continue;
    					if( x+i>=xSize)
    						continue;
    					if( y+j<0)
    						continue;
    					if( y+j>=ySize)
    						continue;
    					lx = x+i;
    					ly = y+j;
    					deltaH = actualH - height[ lx + ly * xSize ];
    					if( deltaH > T )
    					{
    					    
        				    rubble = pct * (deltaH - T);
        				    newheight[ lx + ly * xSize ] = height[ lx + ly *xSize]+rubble;
                            addedDiff += rubble;                    					    
    				    }
    				    //else
//    				        newheight[ lx + ly * xSize ] = height[ lx + ly *xSize];
//    				    printf("\n");
    				}
    			height[ x+y*xSize ] -= addedDiff;
    		}
    	}
    	memcpy( height, newheight, xSize*ySize*sizeof(float) );
	}
	return newheight;

}
*/

// structure that holds the altitude, water amount
// and sediment amount for each vertex
class AWS 
{
public:
  // new_aws->alt = curr_a + kd * curr_s;
  // new_aws->sed = (1.0 - kd) * curr_s;
  void Deposit(float kd)
    {
      alt += kd * sed;
      sed -= (1.0f - kd) * sed;
    }
  // new_aws->alt = curr_a + kd * (curr_s - cs);
  // new_aws->sed = (1.0 - kd) * (curr_s - cs);
  void Deposit(float kd, float cs, float sdump)
    {
      alt += kd * (sdump - cs);
      sed -= (1.0f - kd) * (sdump - cs);
    }
  // new_aws->alt = curr_a - ks * (cs - curr_s);
  // new_aws->sed = 0.0;
  void Erode(float ks, float cs, float sdump)
    {
      alt -= ks * (cs - sdump);
      sed -= sdump;
    }
  void Rain( float rain) 
  { 
    water += rain; 
	//sed += rain*.1;
  }
  AWS() 
  : alt(0.0f)
  , water(0.0f)
  , sed(0.0f) 
  { 
  }
  float alt, water, sed;
};

class DW 
{
  public:
  DW(AWS* cp=0, AWS* np=0, float ad=0.0f) 
  : cptr(cp)
  , nptr(np)
  , adiff(ad) 
  {
  }
  AWS* cptr;
  AWS* nptr;
  float adiff;
};

namespace detail
{
#undef max
#undef min
    inline float max( float a, float b )
    {
        if( a > b )
            return a;
        return b;
    }
    inline float min( float a, float b )
    {
        if( a > b )
            return b;
        return a;
    }
}
class DWP 
{
public:
  DW* operator[](int i) 
  { 
    return dwp + i; 
  }
  void Compute(int ok, float curr_a, float curr_w, int adj)
  {
    if(ok) 
    {
	    float diff = (curr_a + curr_w) - (cptr->alt + cptr->water);
    	if(diff > 0.0f) 
    	{
    	  dwp[n++] = DW(cptr, nptr, diff);
    	  adsum += diff;
    	  maxad = detail::max(maxad, diff);
	    }
    }
    cptr+=adj; 
    nptr+=adj;
  }
  DWP(AWS* cp, AWS* np) 
  : cptr(cp)
  , nptr(np)
  , maxad(0.0f)
  , adsum(0.0f)
  , n(0) 
  { 
  }
  DW dwp[8];   // dw info array
  AWS* cptr;   // pointer to current adjacent vertex
  AWS* nptr;   // pointer to new adjacent vertex
  float maxad;  // maximum altitude difference among all adjacent vertices
  float adsum;  // total difference in altitudes
  int n;       // number of lower adjacent vertices
};

// perform hydraulic ersion on a field
// kc is the sediment capacity for each water particle
//  (i.e. how much sediment it can carry from one vertex to the next)
// kd is the deposition constant (i.e. how much sediment can be dropped
//  at each vertex in 1 iteration)
// ks is the soil softness which controls how much sediment can be
//  washed away by the water.
// iter is the number of iterations to perform
// freq is the frequency of rainfalls (-1 = no rain ever)
// rain is the amount of rain that falls per rainfall
// the algorithm always starts off with 1 rainfall
// sum delta-alts and distribute according to height diff
// what about water which hits a "valley"?  should make lakes and stuff
// scale ks (soil softness according to height?)
float* Rain_Erode( int sx, int sy, int xSize, int ySize, float* height, float lower )
{
	float* ret = (float*)malloc( xSize*ySize*sizeof(float) );
	float* pRet = ret;
	memcpy( ret, height,xSize*ySize*sizeof(float));
	int x = sx;
	int y = sy;
	while( 1 )
	{
		float h = height[ x + y*xSize ];
		float hMin = h;
		int nx = x;
		int ny = y;
    	for( int j = -1; j< 2; ++j )
    		for( int i= -1; i< 2; ++i )
    		{
    			if( i == 0 && j == 0 )
    				continue;
    			if( x+i<0)
    				continue;
    			if( x+i>=xSize)
    				continue;
    			if( y+j<0)
    				continue;
    			if( y+j>=ySize)
    				continue;
				float h1 = height[ x+i+(y+j)*xSize];
				if( h1 < h && h1 < hMin )
				{
					hMin = h1;
					nx = x+i;
					ny = y+j;
				}
			}
		if( nx == x && ny == y )
			break;
		x = nx;
		y = ny;
    	for( int j = -1; j< 2; ++j )
    		for( int i= -1; i< 2; ++i )
    		{
    			if( i == 0 && j == 0 )
    				continue;
    			if( x+i<0)
    				continue;
    			if( x+i>=xSize)
    				continue;
    			if( y+j<0)
    				continue;
    			if( y+j>=ySize)
    				continue;
				ret[ x+i+(y+j)*xSize ] = height[ x+i+(y+j)*xSize]-lower;
			}

	}
	return ret;
}

float* Water_Erode( int xSize, int ySize, float* height, float kc, float kd, float ks, float rain, int iter, int freq )
{
  AWS* curr_aws_array = new AWS[ xSize*ySize ];
  AWS* new_aws_array = new AWS[ xSize*ySize ];
  float omin = 10000.f;
  int w = xSize;
  int h = ySize;
  int wadj = w - 2;
  int i, x, y;

  for(x = 0; x < w*h; ++x ) 
    omin = detail::min( omin, height[x] );
  
  //MinMaxHeights(omin, omax);

  // initialize water, sediment and data arrays
  // make sure all heights are >= 0
  for(x = 0; x < w*h; ++x ) 
  {
    curr_aws_array[x].alt = height[x] - omin;
    curr_aws_array[x].Rain( rain );
  }

  for( i = 0; i < iter; ++i)
  {
    AWS* curr_aws = curr_aws_array;
    AWS* new_aws = new_aws_array;

    for(y = 0; y < h; y++) 
    {
      bool up = (y > 0);
      bool down = (y < h - 1);

      for(x = 0; x < w; x++, curr_aws++, new_aws++) 
      {
	    DWP dwp(curr_aws - w - 1, new_aws - w - 1);
	    bool left = (x > 0);
	    bool right = (x < w - 1);
	    float curr_a = curr_aws->alt;
	    float curr_w = curr_aws->water;

    	// initialize new array data
    	*new_aws = *curr_aws;

    	// top row
    	dwp.Compute(left&&up, curr_a, curr_w, 1);
    	dwp.Compute(up, curr_a, curr_w, 1);
    	dwp.Compute(right&&up, curr_a, curr_w, wadj);

    	// middle row
    	dwp.Compute(left, curr_a, curr_w, 2);
    	dwp.Compute(right, curr_a, curr_w, wadj);
    
    	// bottom row
    	dwp.Compute(left&&down, curr_a, curr_w, 1);
    	dwp.Compute(down, curr_a, curr_w, 1);
    	dwp.Compute(right&&down, curr_a, curr_w, 0);

    	if(!dwp.n) 
    	{
    	  // all adjacent vertices are higher, dump some sediment here
    	  new_aws->Deposit(kd);
    	} 
    	else 
    	{
    	  // amount of water that can be dumped from this vertex
    	  float wdump = detail::min(curr_w, dwp.maxad);
    
    	  // current amount of sediment at this vertex
    	  float curr_s = curr_aws->sed;
    
    	  // pointer to dw info
    	  DW* cdw = dwp[0];
    
    	  // dump all water from this vertex
    	  new_aws->water -= wdump;

    	  // iterate over all lower adjacent vertices
    	  for( int k = dwp.n - 1; k >= 0; --k, ++cdw) 
    	  {
    	    // amount of water that can be dumped to current adj. vertex
    	    float dw = wdump * cdw->adiff / dwp.adsum;
    
    	    // maximum amount of sediment that can be transfered
    	    float sdump = curr_s * cdw->adiff / dwp.adsum;
    
    	    // sediment capacity of current amount of dumped water
    	    float cs = kc * dw;
    
    	    // dump fraction of water to adjacent vertex
    	    cdw->nptr->water = cdw->cptr->water + dw;
    
    	    if(sdump >= cs) 
    	    {
    	      // if there is more sediment than the water can hold
    	      // we deposit the difference at the current vertex
    	      // and dump the maximum amount to the adjacent vertex
    	      cdw->nptr->sed = cdw->cptr->sed + cs;
    	      new_aws->Deposit(kd, cs, sdump);
    	    } 
    	    else 
    	    {
    	      // the water can carry more sediment than is available
    	      // so we erode a little from the current vertex and
    	      // add it to the amount transfered to the adjacent vertex
    	      cdw->nptr->sed = cdw->cptr->sed + sdump + ks * (cs - sdump);
    	      new_aws->Erode(ks, cs, sdump);
    	    }
	      }
	    }
      }
    }
//    tswap(AWS*, new_aws_array, curr_aws_array);
    memcpy(curr_aws_array,new_aws_array,  w*h*sizeof(AWS));

    /* add more rain every freq iterations */
    if(freq > 0 && (i + 1) % freq == 0) 
    {
      for(x = 0; x < w*h; x++)
	    curr_aws_array[x].Rain(rain);
    }
  }

  float* newHeight = (float*)malloc( w*h*sizeof(float) );
  // readjust heights
  for(i = 0; i < w*h; i++)
    newHeight[i] = curr_aws_array[i].alt + omin;

  delete[] curr_aws_array;
  delete[] new_aws_array;
  return newHeight;
}

float* Flatten( bool bSquared, float radius, float strength, float initial, int xSize, int ySize, float* height )
{
	float* ret = (float*)malloc( xSize*ySize*sizeof(float) );
	float* pRet = ret;
	memcpy( ret, height,xSize*ySize*sizeof(float));
	float radiusSqr = radius*radius;
	for( int j = 0; j< ySize; ++j)
	{
		float jSqr = (j-radius)*(j-radius);
		for( int i = 0; i< xSize; ++i, ++pRet )
		{
			float rForce = strength;
			if( !bSquared )
			{
				if( jSqr+(i-radius)*(i-radius) < radiusSqr )
					rForce = strength;
				else
					rForce = 0;

			}

			*pRet -= ( *pRet - initial )*rForce;
		}
	}
	return ret;
}

float* Smooth( bool bSquared, float radius, float strength, int xSize, int ySize, float* height )
{
	float* ret = (float*)malloc( xSize*ySize*sizeof(float) );
	float* pRet = ret;
	memcpy( ret, height,xSize*ySize*sizeof(float));
	float radiusSqr = radius*radius;
	for( int j = 0; j< ySize; ++j)
	{
		float jSqr = (j-radius)*(j-radius);
		for( int i = 0; i< xSize; ++i, ++pRet )
		{
			float rForce = 0.f;
			float distSqr =jSqr+(i-radius)*(i-radius);
			if( distSqr < radiusSqr )
			{
				float ratio = 1.f - sqrt( distSqr ) / radius;
				rForce = sqrt( ratio )*strength;
				

				float rVal = 0.f;
				float nbr=0.f;
				for(int  b = -1; b< 2; ++b )
					for(int  a= -1; a< 2; ++a )
					{
						if( i+a<0)
							continue;
						if( i+a>=xSize)
							continue;
						if( j+b<0)
							continue;
						if( j+b>=ySize)
							continue;
						int lx = a+i;
						int ly = b+j;
						rVal += height[ lx + ly * xSize ];
						nbr += 1.f;
					}
				float newheight = rVal/nbr;
				*pRet += ( newheight - *pRet )*rForce;
			}
		}
	}
	return ret;
}

float* Rougth( bool bSquared, float radius, float strength, int xSize, int ySize, float* height )
{
	float* ret = (float*)malloc( xSize*ySize*sizeof(float) );
	float* pRet = ret;
	memcpy( ret, height,xSize*ySize*sizeof(float));
	float radiusSqr = radius*radius;
	for( int j = 0; j< ySize; ++j)
	{
		float jSqr = (j-radius)*(j-radius);
		for( int i = 0; i< xSize; ++i, ++pRet )
		{
			float rForce = 0.f;
			float distSqr =jSqr+(i-radius)*(i-radius);
			if( distSqr < radiusSqr )
			{
				float ratio = 1.f - sqrt( distSqr ) / radius;
				rForce = sqrt( ratio )*strength;
				

				float rVal = 0.f;
				float nbr=0.f;
				for(int  b = -1; b< 2; ++b )
					for(int  a= -1; a< 2; ++a )
					{
						if( i+a<0)
							continue;
						if( i+a>=xSize)
							continue;
						if( j+b<0)
							continue;
						if( j+b>=ySize)
							continue;
						int lx = a+i;
						int ly = b+j;
						rVal += height[ lx + ly * xSize ];
						nbr += 1.f;
					}
				float newheight = rVal/nbr;
				float delta = (newheight - *pRet );
				if( delta < 0)
					*pRet -= detail::max( -20.f, delta*rForce );
				else
					*pRet -= detail::min( 20.f, delta*rForce );
			}
		}
	}
	return ret;
}

float* NewValley( bool bSquared, float radius, float strength, int xSize, int ySize, float* height )
{
	float* ret = (float*)malloc( xSize*ySize*sizeof(float) );
	float* pRet = ret;
	memcpy( ret, height,xSize*ySize*sizeof(float));
	float radiusSqr = radius*radius;
	for( int j = 0; j< ySize; ++j)
	{
		float jSqr = (j-radius)*(j-radius);
		for( int i = 0; i< xSize; ++i, ++pRet )
		{
			float rForce = 0.f;
			float distSqr =jSqr+(i-radius)*(i-radius);
			if( distSqr < radiusSqr )
			{
				float ratio = 1.f - sqrt( distSqr ) / radius;
				rForce = sqrt( ratio )*strength;
				

				*pRet -= rForce;
			}
		}
	}
	return ret;
}

float* Valley( bool bSquared, float radius, float strength, int xSize, int ySize, float* height )
{
	float* ret = (float*)malloc( xSize*ySize*sizeof(float) );
	float* pRet = ret;
	memcpy( ret, height,xSize*ySize*sizeof(float));
	float radiusSqr = radius*radius;
	for( int j = 0; j< ySize; ++j)
	{
		float jSqr = (j-radius)*(j-radius);
		for( int i = 0; i< xSize; ++i, ++pRet )
		{
			float rForce = 0.f;
			float distSqr =jSqr+(i-radius)*(i-radius);
			if( distSqr < radiusSqr )
			{
				float ratio = 1.f - sqrt( distSqr ) / radius;
				rForce = sqrt( ratio )*strength*radius;
				

				*pRet -= rForce;
			}
		}
	}
	return ret;
}

/*float* MountainsClassic( bool bSquared, float radius, float strength, int xSize, int ySize, float* height )
{
	float* ret = (float*)malloc( xSize*ySize*sizeof(float) );
	float* pRet = ret;
	memcpy( ret, height,xSize*ySize*sizeof(float));
	float radiusSqr = radius*radius;
	for( int j = 0; j< ySize; ++j)
	{
		float jSqr = (j-radius)*(j-radius);
		for( int i = 0; i< xSize; ++i, ++pRet )
		{
			float rForce = 0.f;
			float distSqr =jSqr+(i-radius)*(i-radius);
			if( distSqr < radiusSqr )
			{
				float ratio = 1.f - sqrt( distSqr ) / radius;
				float angle = atan2((float)(j-radius),(float)(i-radius) );
				float dist = sqrt( distSqr )* cos( 8.f*(angle));
				
				rForce = radius*2.f*ratio*cos(dist/radius*3.14156f/2.f)*strength;				
				*pRet += rForce;
			}
		}
	}
	return ret;
}*/

inline float uniform( float a, float b)
{
	int x = rand()&4095;
	float r = (float)x/4095.f;
	r *= (b-a);
	r += a;
	return r;

}
float* MountainsNew( bool bSquared, float radius, float strength, float add, int xSize, int ySize, float* height )
{
	float* ret = (float*)malloc( xSize*ySize*sizeof(float) );
	float* pRet = ret;
	memcpy( ret, height,xSize*ySize*sizeof(float));
	float radiusSqr = radius*radius;
	//add += uniform(.85f,1.15f );
	for( int j = 0; j< ySize; ++j)
	{
		float jSqr = (j-radius)*(j-radius);
		for( int i = 0; i< xSize; ++i, ++pRet )
		{
			float rForce = 0.f;
			float distSqr =jSqr+(i-radius)*(i-radius);
			if( distSqr < radiusSqr )
			{
				float ratio = 1.f - sqrt( distSqr ) / radius;
				float angle = atan2((float)(j-radius),(float)(i-radius) );
				//ratio *= uniform(.85f,1.15f );
				//angle *= uniform(.85f,1.15f );
				float dist = 0;
				if( distSqr < 1.f/3.f * radiusSqr )
					dist = sqrt( distSqr )* cos( 2.f*(angle+add));//*uniform(.85f,1.15f );				
				else if( distSqr < 2.f/3.f * radiusSqr )
					dist = sqrt( distSqr )* cos( 4.f*(angle+add));//*uniform(.85f,1.15f );				
				else
					dist = sqrt( distSqr )* cos( 8.f*(angle+add));//*uniform(.85f,1.15f );				
				dist *= uniform( .75f, 1.f );
				rForce = radius*ratio*cos(dist/radius*3.14156f/2.f)*strength;				
				*pRet += rForce;
			}
		}
	}
	return ret;
}

float* MountainsOld( bool bSquared, float radius, float strength, float add, int xSize, int ySize, float* height )
{
	float* ret = (float*)malloc( xSize*ySize*sizeof(float) );
	float* pRet = ret;
	memcpy( ret, height,xSize*ySize*sizeof(float));
	float radiusSqr = radius*radius;
	//add += uniform(.85f,1.15f );
	for( int j = 0; j< ySize; ++j)
	{
		float jSqr = (j-radius)*(j-radius);
		for( int i = 0; i< xSize; ++i, ++pRet )
		{
			float rForce = 0.f;
			float distSqr =jSqr+(i-radius)*(i-radius);
			if( distSqr < radiusSqr )
			{
				float ratio = 1.f - sqrt( distSqr ) / radius;
				float angle = atan2((float)(j-radius),(float)(i-radius) );
				ratio *= uniform(.85f,1.15f );
				//angle *= uniform(.85f,1.15f );
				float dist = 0;
				dist = sqrt( distSqr )* cos( 8.f*(angle+add))*uniform(.85f,1.15f );				
				rForce = radius*ratio*cos(dist/radius*3.14156f/2.f)*strength;				
				*pRet += rForce;
			}
		}
	}
	return ret;
}

float* CanyonBis( bool bSquared, float radius, float strength,  int xSize, int ySize, float* height )
{
	float* ret = (float*)malloc( xSize*ySize*sizeof(float) );
	float* pRet = ret;
	memcpy( ret, height,xSize*ySize*sizeof(float));
	float radiusSqr = radius*radius;
	for( int j = 0; j< ySize; ++j)
	{
		float jSqr = (j-radius)*(j-radius);
		for( int i = 0; i< xSize; ++i, ++pRet )
		{
			float rForce = 0.f;
			float distSqr =jSqr+(i-radius)*(i-radius);
			if( distSqr < radiusSqr )
			{
				
				float d = sqrt( distSqr );//*uniform(.75f,1.f);
				if (d > radius*.8f)
				{
					float r = radius*.9f;
					d = fabs(r - d);
					//d/=.2f;
					float ratio = 1.f -  d / (radius*.2f);
					if( ratio < 0 )
						ratio = 0;
					if( ratio > 1 )
						ratio = 1;
					r = radius*.1f;
					rForce = -r*.1f*cos(d/r*3.14156f/2.f)*strength;				
					//rForce = -pow( ratio,5.f)*strength*sqrt(radius);
				}
				else
				{
					float ratio = 1.f -  d / radius;
					rForce = pow( ratio,5.f)*strength*sqrt(radius);
				}

				*pRet -= rForce;
			}
		}
	}
	return ret;
}

float* Canyon( bool bSquared, float radius, float strength, float add, int xSize, int ySize, float* height )
{
	float* ret = (float*)malloc( xSize*ySize*sizeof(float) );
	float* pRet = ret;
	memcpy( ret, height,xSize*ySize*sizeof(float));
	float radiusSqr = radius*radius;
	add += uniform(.85f,1.15f );
	for( int j = 0; j< ySize; ++j)
	{
		float jSqr = (j-radius)*(j-radius);
		for( int i = 0; i< xSize; ++i, ++pRet )
		{
			float rForce = 0.f;
			float distSqr =jSqr+(i-radius)*(i-radius);
			if( distSqr < radiusSqr )
			{
				float ratio = 1.f - sqrt( distSqr ) / radius;
				float angle = atan2((float)(j-radius),(float)(i-radius) );
				//ratio *= uniform(.85f,1.15f );
				//angle *= uniform(.85f,1.15f );
				float dist = 0;
				if( distSqr < 1.f/3.f * radiusSqr )
					dist = sqrt( distSqr )* cos( 2.f*(angle+add));//*uniform(.85f,1.15f );				
				else if( distSqr < 2.f/3.f * radiusSqr )
					dist = sqrt( distSqr )* cos( 4.f*(angle+add));//*uniform(.85f,1.15f );				
				else
					dist = sqrt( distSqr )* cos( 8.f*(angle+add));//*uniform(.85f,1.15f );				
				rForce = radius*ratio*cos(dist/radius*3.14156f/2.f)*strength;				
				*pRet -= rForce;
			}
		}
	}
	return ret;
}

float* Hills( bool bSquared, float radius, float strength, int xSize, int ySize, float* height )
{
	float* ret = (float*)malloc( xSize*ySize*sizeof(float) );
	float* pRet = ret;
	memcpy( ret, height,xSize*ySize*sizeof(float));
	float radiusSqr = radius*radius;
	for( int j = 0; j< ySize; ++j)	
	{
		float jSqr = (j-radius)*(j-radius);
		for( int i = 0; i< xSize; ++i, ++pRet )
		{
			float rForce = 0.f;
			float distSqr =jSqr+(i-radius)*(i-radius);
			if( distSqr < radiusSqr )
			{
				//float ratio = 1.f - sqrt( distSqr ) / radius;
				float dist = sqrt( distSqr );
				
				rForce = radius*cos(dist/radius*3.14156f/2.f)*strength;				
				*pRet += rForce;
			}
		}
	}
	return ret;
}

struct Sed
{
	Sed( int _x,int _y,float _dist):x(_x),y(_y),dist(_dist){}
	int x, y;
	float dist;
};

float* BuildDistanceMap( int xSize, int ySize, unsigned char* height, unsigned char value )
{
	std::vector< Sed > seed;
	char* done = new char[ xSize*ySize ];
	memset( done, 0, xSize*ySize );
	float* distances = (float*)malloc( xSize*ySize *sizeof(float) );
	for( int y = 0; y < ySize; ++y )
		for( int x = 0; x < xSize; ++x )
		{
			if( height[ x + y*xSize ]==value )
			{
				seed.push_back( Sed( x,y,0.f ) );
				distances[ x+y*xSize ] = 0.f;
				done[ x+y*xSize ] = true;
			}
			else
				distances[ x+y*xSize ] = 100000.f;
		}
	float const2sqr = sqrt( 2. );
	for( int i = 0; i< seed.size(); ++i )
	{
		Sed& p = seed[i];
		Sed added[] = { Sed( p.x,p.y+1,p.dist+1.f ), Sed( p.x,p.y-1,p.dist+1.f ),Sed( p.x+1,p.y,p.dist+1.f ),Sed( p.x-1,p.y,p.dist+1.f ) };
		Sed* v = added;
		for( int j = 0; j<4; ++j, ++v )
		{
			if( v->x < 0 )
				continue;
			if( v->y < 0 )
				continue;
			if( v->x >= xSize )
				continue;
			if( v->y >= ySize )
				continue;
			int offset = v->x+v->y*xSize;
			if( done[ offset ] == true )
				continue;
			if( height[ offset ] > 0.f )
				continue;
			done[ offset ] = true;
			distances[ offset ] = v->dist;
			seed.push_back( *v );
		}
	}
	delete[] done;

	return distances;
}

unsigned char* UseDistMap( int xSize, int ySize, std::map< int, float*> distances )
{
	unsigned char* heights = (unsigned char*)malloc( xSize*ySize );
	for( int y = 0; y < ySize; ++y )
		for( int x = 0; x < xSize; ++x )
		{
			int offset = x+y*xSize;
			std::map< int, float > dists;
			{
				std::map< int, float* >::iterator it = distances.begin();
				std::map< int, float* >::iterator itEnd = distances.end();
				while( it != itEnd )
				{
					float h = it->second[ offset ];
					if( h < 100000.f )
					{
						dists.insert( std::make_pair( it->first,h ) );
					}
					++it;
				}
			}
			float h;
			if( dists.size() == 0 )
				h = 0.f;
			else if( dists.size() == 1)
			{
				h = dists.begin()->first;
			}
			else
			{
				std::map< int, float >::iterator it = dists.begin();
				std::map< int, float >::iterator itEnd = dists.end();
				float distTotal = 0.f;
				float height = 0.f;
				while( it != itEnd )
				{
					distTotal += it->second;
					++it;
				}
				it = dists.begin();
				while( it != itEnd )
				{
					float w = ((float)it->first)*detail::max( 0.f, distTotal-it->second );
					height += w;
					++it;
				}
				h = height/distTotal;				
			}
			heights[ offset ] = h;
		}
	return heights;
}


std::map< int, float* > ConvertToMap( PyObject* p )
{
	std::map< int, float* > result;
	if( PyDict_Check( p ) )
	{
		PyObject *key, *value;
		int pos = 0;

		while (PyDict_Next(p, &pos, &key, &value)) 
		{
			int k ;
			if( PyInt_Check( key ) )
			{
//				printf("key ok %d\n",PyInt_AsLong( key ) );
				k = PyInt_AsLong( key );
			}
			else
				printf("key not ok\n" );
			if( PyString_Check( value ) )
			{
//				printf("value ok size = %d\n", PyString_Size( value ) );
				char* buf;
				int size;
				PyString_AsStringAndSize( value, &buf, &size );
				result.insert( std::make_pair( k, (float*)buf ) );				
			}
			else
				printf("value not ok\n" );
		}


	}
	return result;
}

unsigned char* GenerateImage( float waterLevel,int xSize, int ySize, float* heights, unsigned char* colors, int* pMinx,int* pMiny,int* pMaxx,int* pMaxy )
{
	int* minYmap = new int[514];
	int* maxYmap = new int[514];
	memset( maxYmap, 0, 514*4 );
	memset( minYmap, 0x7f, 514*4 );
	unsigned char* im = (unsigned char*)malloc( 514*428*6 );
	memset( im, 0, 514*428*6 );
    int miny  = 428;
    int maxy = 0;
    int minx  = 514;
    int maxx = 0;
	int secondOffset = 514*428*3;
	for( int y = 0; y < ySize; ++y )
		for( int x = 0; x < xSize; ++x )
		{
			float x2 = float(x)*(512.f-150.f)/256.f + 150.f-(150.f*float(y)/256.f);
			float y2 = float(y)*(181.f)/256.f+75.f*float(x)/256.f;
			float yBase = y2;
			float h = heights[ y*xSize + x ];
			if( h < waterLevel )
				h = waterLevel;

			h  *= 21.f/250.f;
			y2 -= h;
			y2 += 428-256;
			yBase += 428-256;
			
			if( y2 < 0.f )
				y2 = 0.f;
			if( y2 < miny )
				miny = y2;
			if( yBase > maxy )
				maxy = yBase;
			if(x2 < minx)
				minx = x2;
			if (x2 > maxx)
				maxx = x2;
			if( minYmap[ (int)x2 ] > y2 )
				minYmap[ (int)x2 ] = (int)y2;
			if( maxYmap[ (int)x2 ] < y2 )
				maxYmap[ (int)x2 ] = (int)y2;
			unsigned char r = colors[(y*xSize+x)*3+0];
			unsigned char g = colors[(y*xSize+x)*3+1];
			unsigned char b = colors[(y*xSize+x)*3+2];
			/*r/=2;
			g/=2;
			b/=2;*/
			for( int j = (int)y2; j<(int)yBase;++j)
			{
				im[ ((int)x2+((int)j)*514)*3+0 ]=r; 
				im[ ((int)x2+((int)j)*514)*3+1 ]=g; 
				im[ ((int)x2+((int)j)*514)*3+2 ]=b; 
				im[ secondOffset+((int)x2+((int)j)*514)*3+2 ]=255;
			}
		}
	for( int x = minx; x < maxx; ++x )
	{
		im[ secondOffset+(x+(minYmap[x])*514)*3+0 ]=255;
		im[ secondOffset+(x+(minYmap[x])*514)*3+1 ]=255;
		im[ secondOffset+(x+(maxYmap[x])*514)*3+0 ]=255;
		im[ secondOffset+(x+(maxYmap[x])*514)*3+1 ]=255;
	}
	*pMinx = minx;
	*pMiny = miny;
	*pMaxx = maxx;
	*pMaxy = maxy;
	delete[] minYmap;
	delete[] maxYmap;
	return im;

}

class PySpline
	: public Spline
{
    bool bRad_;
    bool bPertubRad_;
    bool bPertubHeight_;
    float rPRMin_;
    float rPRMax_;
    float rPHMin_;
    float rPHMax_;
public:
	explicit PySpline( PyObject* p )
	: Spline()
	, bRad_( false )
	, bPertubRad_( false )
	, bPertubHeight_( false )
	{
	    if( PyDict_Check(p) )
	    {
    		PyObject *key, *value;
    		int pos = 0;
    
    		while (PyDict_Next(p, &pos, &key, &value)) 
    		{
    		    char* szKey;
    			if( PyString_Check( key ) )
    			{
    				szKey = PyString_AsString( key );
    			}
    			if( !strcmp( szKey, "pertubHeight" ) )
    			{
   			    
        			if( PyList_Check( value ) )
        			{
        			    bPertubHeight_ = true;
        			    rPHMin_ = PyFloat_AsDouble( PyList_GetItem( value,0 ) );
        			    rPHMax_ = PyFloat_AsDouble( PyList_GetItem( value,1 ) );
        			    printf ("Perturbation heihgt : %.02f,%.02f\n",rPHMin_,rPHMax_ );
    			    }
    			}
    			else if( !strcmp( szKey, "pertubRadius" ) )
    			{
    			    
        			if( PyList_Check( value ) )
        			{
        			    bPertubRad_ = true;
        			    rPRMin_ = PyFloat_AsDouble( PyList_GetItem( value,0 ) );
        			    rPRMax_ = PyFloat_AsDouble( PyList_GetItem( value,1 ) );
        			    printf ("Perturbation radius : %.02f,%.02f\n",rPRMin_,rPRMax_ );
    			    }
    			}
    			else if( !strcmp( szKey, "factor" ) )
    			    bRad_ = true;
                else if( !strcmp( szKey, "spline" ) )
    			{
                	if( PyList_Check( value ) )
                	{
            			int n= PyList_Size( value );
            			for (int i = 0; i< n; ++i )
            			{
            				PyObject* cp = PyList_GetItem( value, i );
            				if( PyTuple_Check( cp ) && PyTuple_Size(cp) == 2)
            				{
            					if( PyFloat_Check( PyTuple_GetItem( cp, 0 ) ) &&  PyFloat_Check( PyTuple_GetItem( cp, 1 ) ) )
            					{
            						float x = PyFloat_AsDouble( PyTuple_GetItem( cp, 0 ) );
            						float y = PyFloat_AsDouble( PyTuple_GetItem( cp, 1 ) );
            						AddControl( D3DXVECTOR2( x,y ) );
            						printf( "added : %.02f - %.02f\n",x,y );
            					}
            				}
            			}
                    }        
                }
            }
            printf("----\n" );
    		Init();
    	}
	}
	
	float PertubHeight()
	{
	    if( !bPertubHeight_ )
	        return 1.f;
	    return uniform( rPHMin_, rPHMax_ );
	}
	float PertubRadius()
	{
	    if( !bPertubRad_ )
	        return 1.f;
	    return uniform( rPRMin_, rPRMax_ );
	}
	float ScaleByRadius( float rRadius )
	{
	    if( bRad_ )
	        return rRadius;
	    return 1.f;
	}
};


float* Universal( bool bSquared, float radius, float strength, int xSize, int ySize, float* height, PySpline& shape )
{	
	float* ret = (float*)malloc( xSize*ySize*sizeof(float) );
	float* pRet = ret;
	memcpy( ret, height,xSize*ySize*sizeof(float));
	float radiusSqr = radius*radius;
	std::vector< float > v;
	v.resize( 100 );
	for( int i = 0; i< 100; ++i )
	{
		float a = shape[ (float)i/100.f ];
		v[i] = a;
	}
	for( int j = 0; j< ySize; ++j)	
	{
		float jSqr = (j-radius)*(j-radius);
		for( int i = 0; i< xSize; ++i, ++pRet )
		{
			float rForce = 0.f;
			float distSqr =jSqr+(i-radius)*(i-radius);
			if( distSqr < radiusSqr )
			{
				float ratio = sqrt( distSqr )*shape.PertubRadius() / radius;
				if( ratio > 1.f )
				    ratio = 1.f;
				
				//rForce = (v[ int(ratio*100.f) ]*strength);				
				float a= v[ (int)(ratio*100.f) ];
				a = a*shape.PertubHeight();
				rForce = a*strength*shape.ScaleByRadius( radius );
				*pRet += rForce;
			}
		}
	}
	return ret;
}

unsigned char* GetShapeImage( PySpline& shape )
{
	std::vector< float > v;
	v.resize( 50 );
	for( int i = 0; i< 50; ++i )
	{
		float a = shape[ (float)i/50.f ];
		v[i] = a;
	}
	unsigned char* pImg = (unsigned char* )malloc( 50*50*3 );
	memset( pImg, 0, 50*50*3 );
	for( int i = 0; i< 50; ++i )
	{
		float y = v[i];
		y*=10;
		y+=25;
		y=50-y;
		if( y > 49 )
			y = 49;
		if( y < 0 )
			y = 0;

		pImg[ (i + (int)25*50)*3 ] = 0xFF;
		pImg[ (i + (int)y*50)*3 ] = 0xFF;
		pImg[ (i + (int)y*50)*3+1 ] = 0xFF;
		pImg[ (i + (int)y*50)*3+2 ] = 0xFF;
	}
	return pImg;
}

extern "C"
{

static PyObject *Py_GenNormal( PyObject *self, PyObject *args )
{
	char* buffer;
	int len;
	unsigned char* out;
	PyObject *pRet ;
	int xSize, ySize;
//	fflush( stdout );
	if (!PyArg_ParseTuple(args, "(ii)s#", &ySize,&xSize,&buffer, &len))
        return NULL;
	
	Py_BEGIN_ALLOW_THREADS
	out = (unsigned char*)GenerateNormal( xSize, ySize, (float*)buffer );
	Py_END_ALLOW_THREADS
	
	pRet = Py_BuildValue( "s#", out, len*3 ); 
	free( out );
    return pRet;
}

static PyObject *Py_GenShadow( PyObject *self, PyObject *args )
{
	char* bufferH;
	char* bufferN;
	int lenH,lenN, lenS;
	float lightDir[3];
	unsigned char* bufferS;
	PyObject *pRet ;
	int bLight;
	int xSize, ySize;
	int yStart, yMax;
	if (!PyArg_ParseTuple(args, "i(ii)(fff)(ii)s#s#s#", &bLight, &yStart,&yMax,&lightDir[0],&lightDir[1],&lightDir[2],&ySize,&xSize, &bufferH, &lenH, &bufferN, &lenN, &bufferS, &lenS ))
        return NULL;
//    printf("shadow finished\n");        
//    fflush( stdout );	
	Py_BEGIN_ALLOW_THREADS

	GenerateShadow( bLight, yStart,yMax,xSize, ySize, lightDir,(float*)bufferH,(float*)bufferN, bufferS );
	Py_END_ALLOW_THREADS
	//pRet = Py_BuildValue( "s#", out, xSize*ySize ); 
//	fflush( stdout );
	//free( out );
	Py_INCREF(Py_None);
    return Py_None;

    return pRet;
}

static PyObject *Py_OnePassColors( PyObject *self, PyObject *args )
{
	char* bufferH;
	int lenH;
	float waterLevel;
	float lightDir[3];
	unsigned char* out;
	PyObject *pRet ;
	PyObject *pWGrad ;
	PyObject *pLGrad ;
	int bLight;
	int xSize, ySize;
	if (!PyArg_ParseTuple(args, "i(ii)fs#OO(fff)", &bLight,&ySize,&xSize, &waterLevel, &bufferH, &lenH, &pWGrad,&pLGrad,&lightDir[0], &lightDir[1],&lightDir[2] ) )
        return NULL;
	Py_BEGIN_ALLOW_THREADS
	out = ( unsigned char*)OnePassColors( bLight, xSize, ySize, waterLevel, (float*)bufferH, Gradient( pWGrad ), Gradient( pLGrad ), lightDir );
	Py_END_ALLOW_THREADS
	pRet = Py_BuildValue( "s#", out, xSize*ySize*3 ); 
	free( out );
    return pRet;
}


static PyObject *Py_GenColors( PyObject *self, PyObject *args )
{
	char* bufferH;
	char* bufferN;
	char* bufferS;
	int lenH,lenN,lenS;
	float waterLevel;
	unsigned char* out;
	PyObject *pRet ;
	PyObject *pWGrad ;
	PyObject *pLGrad ;
	int xSize, ySize;

	//    printf("colors in");
//    fflush( stdout );
	if (!PyArg_ParseTuple(args, "(ii)fs#s#s#OO", &ySize,&xSize, &waterLevel, &bufferH, &lenH, &bufferN, &lenN, &bufferS, &lenS,&pWGrad,&pLGrad ))
        return NULL;
//    printf("%d %d - lenH = %d ; lenN = %d ; lenS = %d\n",xSize,ySize,lenH, lenN,lenS );
//    fflush( stdout );
	
	Py_BEGIN_ALLOW_THREADS
	out = (unsigned char*)GenerateColors( xSize, ySize, waterLevel,(float*)bufferH,(float*)bufferN,(unsigned char*)bufferS, Gradient( pWGrad ), Gradient( pLGrad ) );
	Py_END_ALLOW_THREADS
	pRet = Py_BuildValue( "s#", out, xSize*ySize*3 ); 
	free( out );
    return pRet;
}

static PyObject* Py_Universal( PyObject *self, PyObject *args )
{
	char bSquared;
	int radius;
	float strength;
	int xSize,ySize;
	char* bufferH;
	int lenH;
	unsigned char* out;
	PyObject* pSpline;
	PyObject* pRet;
	if (!PyArg_ParseTuple(args, "bif(ii)s#O", &bSquared,&radius,&strength,&ySize,&xSize, &bufferH, &lenH,&pSpline))
        return NULL;
	PySpline shape( pSpline );
	out = ( unsigned char*)Universal( bSquared,radius,strength,xSize, ySize, (float*)bufferH, shape);
	pRet = Py_BuildValue( "s#", out, lenH ); 
	free( out );	
    return pRet;
}


static PyObject* Py_Egalise( PyObject *self, PyObject *args )
{
	char* bufferH;
	int lenH;
	PyObject *pRet ;
	int xSize, ySize;
	unsigned char* out;
	if (!PyArg_ParseTuple(args, "(ii)s#", &ySize,&xSize, &bufferH, &lenH))
        return NULL;

	out = ( unsigned char*)Egalize( xSize, ySize, (float*)bufferH );
//	printf( "egalize return\n");fflush( stdout );
	pRet = Py_BuildValue( "s#", out, lenH ); 
//	printf( "egalize build done\n");fflush( stdout );
	free( out );	
//	printf( "egalize free done\n");fflush( stdout );
	//free( bufferH );	
    return pRet;
}

static PyObject* Py_WErode( PyObject *self, PyObject *args )
{
	char* bufferH;
	int lenH;
	float talus,pct;
	PyObject *pRet ;
	int xSize, ySize,iter;
	unsigned char* out;
	if (!PyArg_ParseTuple(args, "ffi(ii)s#", &talus,&pct,&iter,&ySize,&xSize, &bufferH, &lenH))
        return NULL;
	out = ( unsigned char*)WeatherErosion( xSize, ySize, (float*)bufferH, talus,pct,iter );
	pRet = Py_BuildValue( "s#", out, lenH ); 
	free( out );	
    return pRet;
}

static PyObject* Py_WaterErode( PyObject *self, PyObject *args )
{
    int xSize;
    int ySize;
    char* bufferH;
    int lenH;
    unsigned char* out;
    float kc,kd, ks;
    float rain;
    int iter;
    int freq;
    PyObject* pRet;
	if (!PyArg_ParseTuple(args, "ffffii(ii)s#", &kc,&kd,&ks,&rain,&iter,&freq,&ySize,&xSize, &bufferH, &lenH))
        return NULL;
	out = ( unsigned char*)Water_Erode( xSize, ySize, (float*)bufferH, kc, kd, ks, rain, iter, freq );
	pRet = Py_BuildValue( "s#", out, lenH ); 
	free( out );	
    return pRet;
}
static PyObject* Py_RainErode( PyObject *self, PyObject *args )
{
    int xSize;
    int ySize;
    char* bufferH;
    int lenH;
    unsigned char* out;
    float kc,kd, ks;
    float rain;
    int iter;
    int freq;
	int xs,ys;
	float lower;
    PyObject* pRet;
	if (!PyArg_ParseTuple(args, "(ii)f(ii)s#", &xs,&ys,&lower,&ySize,&xSize, &bufferH, &lenH))
        return NULL;
	out = ( unsigned char*)Rain_Erode( xs,ys,xSize, ySize, (float*)bufferH, lower );
	pRet = Py_BuildValue( "s#", out, lenH ); 
	free( out );	
    return pRet;
}

static PyObject* Py_Flatten( PyObject *self, PyObject *args )
{
	char bSquared;
	int radius;
	float strength;
	float initial;
	int xSize,ySize;
	char* bufferH;
	int lenH;
	unsigned char* out;
	PyObject* pRet;
	if (!PyArg_ParseTuple(args, "biff(ii)s#", &bSquared,&radius,&strength,&initial,&ySize,&xSize, &bufferH, &lenH))
        return NULL;
	out = ( unsigned char*)Flatten( bSquared,radius,strength,initial,xSize, ySize, (float*)bufferH);
	pRet = Py_BuildValue( "s#", out, lenH ); 
	free( out );	
    return pRet;
}

static PyObject* Py_Smooth( PyObject *self, PyObject *args )
{
	char bSquared;
	int radius;
	float strength;
	int xSize,ySize;
	char* bufferH;
	int lenH;
	unsigned char* out;
	PyObject* pRet;
	if (!PyArg_ParseTuple(args, "bif(ii)s#", &bSquared,&radius,&strength,&ySize,&xSize, &bufferH, &lenH))
        return NULL;
	out = ( unsigned char*)Smooth( bSquared,radius,strength,xSize, ySize, (float*)bufferH);
	pRet = Py_BuildValue( "s#", out, lenH ); 
	free( out );	
    return pRet;
}

static PyObject* Py_Rough( PyObject *self, PyObject *args )
{
	char bSquared;
	int radius;
	float strength;
	int xSize,ySize;
	char* bufferH;
	int lenH;
	unsigned char* out;
	PyObject* pRet;
	if (!PyArg_ParseTuple(args, "bif(ii)s#", &bSquared,&radius,&strength,&ySize,&xSize, &bufferH, &lenH))
        return NULL;
	out = ( unsigned char*)Rougth( bSquared,radius,strength,xSize, ySize, (float*)bufferH);
	pRet = Py_BuildValue( "s#", out, lenH ); 
	free( out );	
    return pRet;
}

static PyObject* Py_Valley( PyObject *self, PyObject *args )
{
	char bSquared;
	int radius;
	float strength;
	int xSize,ySize;
	char* bufferH;
	int lenH;
	unsigned char* out;
	PyObject* pRet;
	if (!PyArg_ParseTuple(args, "bif(ii)s#", &bSquared,&radius,&strength,&ySize,&xSize, &bufferH, &lenH))
        return NULL;
	out = ( unsigned char*)Valley( bSquared,radius,strength,xSize, ySize, (float*)bufferH);
	pRet = Py_BuildValue( "s#", out, lenH ); 
	free( out );	
    return pRet;
}
static PyObject* Py_NewValley( PyObject *self, PyObject *args )
{
	char bSquared;
	int radius;
	float strength;
	int xSize,ySize;
	char* bufferH;
	int lenH;
	unsigned char* out;
	PyObject* pRet;
	if (!PyArg_ParseTuple(args, "bif(ii)s#", &bSquared,&radius,&strength,&ySize,&xSize, &bufferH, &lenH))
        return NULL;
	out = ( unsigned char*)NewValley( bSquared,radius,strength,xSize, ySize, (float*)bufferH);
	pRet = Py_BuildValue( "s#", out, lenH ); 
	free( out );	
    return pRet;
}

/*
static PyObject* Py_MountainsClassic( PyObject *self, PyObject *args )
{
	char bSquared;
	int radius;
	float strength;
	int xSize,ySize;
	char* bufferH;
	int lenH;
	unsigned char* out;
	PyObject* pRet;
	if (!PyArg_ParseTuple(args, "bif(ii)s#", &bSquared,&radius,&strength,&ySize,&xSize, &bufferH, &lenH))
        return NULL;
	out = ( unsigned char*)MountainsClassic( bSquared,radius,strength,xSize, ySize, (float*)bufferH);
	pRet = Py_BuildValue( "s#", out, lenH ); 
	free( out );	
    return pRet;
}*/

static PyObject* Py_MountainsOld( PyObject *self, PyObject *args )
{
	char bSquared;
	int radius;
	float strength;
	float add;
	int xSize,ySize;
	char* bufferH;
	int lenH;
	unsigned char* out;
	PyObject* pRet;
	if (!PyArg_ParseTuple(args, "biff(ii)s#", &bSquared,&radius,&strength,&add,&ySize,&xSize, &bufferH, &lenH))
        return NULL;
	out = ( unsigned char*)MountainsOld( bSquared,radius,strength,add,xSize, ySize, (float*)bufferH);
	pRet = Py_BuildValue( "s#", out, lenH ); 
	free( out );	
    return pRet;
}

static PyObject* Py_MountainsNew( PyObject *self, PyObject *args )
{
	char bSquared;
	int radius;
	float strength;
	float add;
	int xSize,ySize;
	char* bufferH;
	int lenH;
	unsigned char* out;
	PyObject* pRet;
	if (!PyArg_ParseTuple(args, "biff(ii)s#", &bSquared,&radius,&strength,&add,&ySize,&xSize, &bufferH, &lenH))
        return NULL;
	out = ( unsigned char*)MountainsNew( bSquared,radius,strength,add,xSize, ySize, (float*)bufferH);
	pRet = Py_BuildValue( "s#", out, lenH ); 
	free( out );	
    return pRet;
}

static PyObject* Py_Canyon( PyObject *self, PyObject *args )
{
	char bSquared;
	int radius;
	float strength;
	float add;
	int xSize,ySize;
	char* bufferH;
	int lenH;
	unsigned char* out;
	PyObject* pRet;
	if (!PyArg_ParseTuple(args, "biff(ii)s#", &bSquared,&radius,&strength,&add,&ySize,&xSize, &bufferH, &lenH))
        return NULL;
	out = ( unsigned char*)Canyon( bSquared,radius,strength,add,xSize, ySize, (float*)bufferH);
	pRet = Py_BuildValue( "s#", out, lenH ); 
	free( out );	
    return pRet;
}

static PyObject* Py_CanyonBis( PyObject *self, PyObject *args )
{
	char bSquared;
	int radius;
	float strength;
	int xSize,ySize;
	char* bufferH;
	int lenH;
	unsigned char* out;
	PyObject* pRet;
	if (!PyArg_ParseTuple(args, "bif(ii)s#", &bSquared,&radius,&strength,&ySize,&xSize, &bufferH, &lenH))
        return NULL;
	out = ( unsigned char*)CanyonBis( bSquared,radius,strength,xSize, ySize, (float*)bufferH);
	pRet = Py_BuildValue( "s#", out, lenH ); 
	free( out );	
    return pRet;
}

static PyObject* Py_Hills( PyObject *self, PyObject *args )
{
	char bSquared;
	int radius;
	float strength;
	int xSize,ySize;
	char* bufferH;
	int lenH;
	unsigned char* out;
	PyObject* pRet;
	if (!PyArg_ParseTuple(args, "bif(ii)s#", &bSquared,&radius,&strength,&ySize,&xSize, &bufferH, &lenH))
        return NULL;
	out = ( unsigned char*)Hills( bSquared,radius,strength,xSize, ySize, (float*)bufferH);
	pRet = Py_BuildValue( "s#", out, lenH ); 
	free( out );	
    return pRet;
}


static PyObject* Py_Expand( PyObject *self, PyObject *args )
{
	int xSize,ySize;
	char* bufferH;
	int lenH;
	unsigned char* out;
	PyObject* pRet;
	if (!PyArg_ParseTuple(args, "(ii)s#", &ySize,&xSize, &bufferH, &lenH))
        return NULL;
	out = ( unsigned char*)expand( xSize, ySize,(unsigned char* )bufferH);
	pRet = Py_BuildValue( "s#", out, lenH ); 
	free( out );	
    return pRet;
}

static PyObject* Py_BuildDistMap( PyObject *self, PyObject *args )
{
	int xSize,ySize;
	char* bufferH;
	int lenH;
	int nValue;
	unsigned char* out;
	PyObject* pRet;
	if (!PyArg_ParseTuple(args, "(ii)s#i", &ySize,&xSize, &bufferH, &lenH,&nValue))
        return NULL;
	out = ( unsigned char*)BuildDistanceMap( xSize, ySize,(unsigned char* )bufferH, nValue);
	pRet = Py_BuildValue( "s#", out, xSize*ySize*sizeof(float) ); 
	free( out );	
    return pRet;
}

static PyObject* Py_UseDistancesMap( PyObject *self, PyObject *args )
{
	int xSize,ySize;
	PyObject* pDict;
	unsigned char* out;
	PyObject* pRet;
	if (!PyArg_ParseTuple(args, "O(ii)", &pDict, &ySize,&xSize))
        return NULL;
	out = UseDistMap( xSize, ySize, ConvertToMap( pDict ) );

	pRet = Py_BuildValue( "s#", out, xSize*ySize ); 
	free( out );	
    return pRet;
}

static PyObject* Py_GenerateImage( PyObject *self, PyObject *args )
{
	int xSize,ySize,lenH,lenC;
	char* bufH;
	char* bufC;
	unsigned char* out;
	float waterLevel;
	int xmin,ymin,xmax,ymax;
	PyObject* pRet;
	if (!PyArg_ParseTuple(args, "f(ii)s#s#", &waterLevel,&ySize,&xSize,&bufH,&lenH,&bufC,&lenC))
        return NULL;
	out = GenerateImage( waterLevel,xSize, ySize,(float*)bufH,(unsigned char*)bufC,&xmin,&ymin,&xmax,&ymax );
	pRet = Py_BuildValue( "iiiis#", xmin,ymin,xmax,ymax,out,514*428*6 ); 
	free( out );	
    return pRet;
}

static PyObject* Py_GetShapeImage( PyObject *self, PyObject *args )
{
	unsigned char* out;
	PyObject* pSpline;
	PyObject* pRet;
	if (!PyArg_ParseTuple(args, "O", &pSpline))
        return NULL;
	PySpline shape( pSpline );
	out = GetShapeImage( shape );
	pRet = Py_BuildValue( "s#", out,50*50*3 ); 
	free( out );	
    return pRet;
}

static PyObject* PyT_GetVersion( PyObject *self, PyObject *args )
{
	PyObject* pRet;
	pRet = Py_BuildValue( "s", "v1.0c" );
	return pRet;
}

static PyMethodDef tools3DMethods[] =
{
	{"generateNormals", Py_GenNormal, METH_VARARGS, "generate normal map" },
	{"generateShadows", Py_GenShadow, METH_VARARGS, "generate shadow map" },
	{"generateColors", Py_GenColors, METH_VARARGS, "generate color map" },
	{"onePassColors", Py_OnePassColors, METH_VARARGS, "generate color map" },
	{"egalize", Py_Egalise, METH_VARARGS, "egalise a map" },
	{"weatherErode", Py_WErode, METH_VARARGS, "erode a map" },
 	{"waterErode", Py_WaterErode, METH_VARARGS, "erode a map hydro" },
	{"rainErode", Py_RainErode, METH_VARARGS, "erode a map hydro" },
	{"flatten", Py_Flatten, METH_VARARGS, "flatten a map" },
	{"smooth", Py_Smooth, METH_VARARGS, "smooth a map" },
	{"rough", Py_Rough, METH_VARARGS, "smooth a map" },
	{"valley", Py_Valley, METH_VARARGS, "make a valley" },
	{"newValley", Py_NewValley, METH_VARARGS, "make a valley" },
	{"mountainsOld", Py_MountainsOld, METH_VARARGS, "make a mountain" },
	{"mountainsNew", Py_MountainsNew, METH_VARARGS, "make a mountain" },
	{"canyon", Py_Canyon, METH_VARARGS, "make a canyon" },
	{"canyonBis", Py_CanyonBis, METH_VARARGS, "make a canyon" },
	{"hills", Py_Hills, METH_VARARGS, "make a hill" },
	{"expand", Py_Expand, METH_VARARGS, "expand isolines" },
	{"buildDistanceMap", Py_BuildDistMap, METH_VARARGS, "buildDistanceMap" },
	{"useDistancesMap", Py_UseDistancesMap, METH_VARARGS, "UseDistancesMap" },
	{"generateImage", Py_GenerateImage, METH_VARARGS, "generate thumbs" },
	{"universal", Py_Universal, METH_VARARGS, "universal shape tool" },
	{"getShapeUniversal", Py_GetShapeImage, METH_VARARGS, "universal shape image" },
	{"GetVersion", PyT_GetVersion,METH_VARARGS,"get dll version" },
	
	
    {NULL, NULL, 0, NULL}        /* Sentinel */
};


_declspec( dllexport ) void  inittools3D(void)
{
	TestSpline();
    (void) Py_InitModule("tools3D", tools3DMethods);
}

}