// Sample effect file

// transformations
float4x4 WorldViewProj : WORLDVIEWPROJECTION;

texture landTex1 < string name = "datas/detail.bmp"; >;

float texSizeX = 769;
float texSizeY = 769;

sampler land1 = sampler_state 
{
    texture = <landTex1>;
    AddressU  = WRAP;        
    AddressV  = WRAP;
    AddressW  = WRAP;
    MIPFILTER = LINEAR;
    MINFILTER = LINEAR;
    MAGFILTER = LINEAR;
};


struct VS_COMBINE3
{
    float4 Pos  : POSITION;
    float4 diffuse : COLOR0;
    float2 texDetColor : TEXCOORD0;
};

VS_COMBINE3 CombineVS3( float4 Pos : POSITION, float2 texColor : TEXCOORD0, float4 color : COLOR0 )
{
    VS_COMBINE3 output = (VS_COMBINE3)0;
    output.Pos = mul(Pos, WorldViewProj);    // position (view space)    
    
	//output.texColor = texColor;
	output.diffuse = color;
    output.texDetColor = float2( Pos.x/(texSizeX*12/32), Pos.z/(texSizeY*12/32) ); 
    //output.texDetColor = float2( Pos.x/12, Pos.z/12); 

    return output;
}

float4 CombinePS3( VS_COMBINE3 In ) : COLOR0
{
    //float4 color = tex2D( land0, In.texColor )*tex2D( land1, In.texDetColor )*2;
    float4 color = (In.diffuse*2)*tex2D( land1, In.texDetColor );
    return color;   
}

technique tec
{
    pass p0
    {
        alphablendenable = false;
        srcblend = srccolor;
        destblend = invsrccolor;
		//FillMode=WireFrame;
		  CullMode = CW;
        VertexShader = compile vs_1_1 CombineVS3();
        PixelShader = compile ps_1_1 CombinePS3();
    }
}

technique FP
{
  pass p0
  {
    lighting = false;
    colorvertex=true;
    EMISSIVEMATERIALSOURCE=color1;
    cullmode=cw;
    texture[0]=<landTex1>;
    ColorArg1[0]=CURRENT;
    ColorArg2[0]=TEXTURE;
    ColorOp[0]=MODULATE;
    
  }
}
