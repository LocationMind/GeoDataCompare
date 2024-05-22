PGDMP  1        
            |            overturemap    16.2    16.2                0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false                       0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false                       0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false                       1262    125791    overturemap    DATABASE     �   CREATE DATABASE overturemap WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'English_United States.932';
    DROP DATABASE overturemap;
                postgres    false            �            1259    544821    bounding_box    TABLE     �   CREATE TABLE public.bounding_box (
    id integer NOT NULL,
    geom public.geometry,
    wkt_geom character varying,
    name character varying
);
     DROP TABLE public.bounding_box;
       public         heap    postgres    false            �            1259    544820    bounding_box_id_seq    SEQUENCE     �   CREATE SEQUENCE public.bounding_box_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 *   DROP SEQUENCE public.bounding_box_id_seq;
       public          postgres    false    228                       0    0    bounding_box_id_seq    SEQUENCE OWNED BY     K   ALTER SEQUENCE public.bounding_box_id_seq OWNED BY public.bounding_box.id;
          public          postgres    false    227            l           2604    544824    bounding_box id    DEFAULT     r   ALTER TABLE ONLY public.bounding_box ALTER COLUMN id SET DEFAULT nextval('public.bounding_box_id_seq'::regclass);
 >   ALTER TABLE public.bounding_box ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    227    228    228            
          0    544821    bounding_box 
   TABLE DATA           @   COPY public.bounding_box (id, geom, wkt_geom, name) FROM stdin;
    public          postgres    false    228                     0    0    bounding_box_id_seq    SEQUENCE SET     A   SELECT pg_catalog.setval('public.bounding_box_id_seq', 1, true);
          public          postgres    false    227            p           2606    544828    bounding_box bounding_box_pkey 
   CONSTRAINT     \   ALTER TABLE ONLY public.bounding_box
    ADD CONSTRAINT bounding_box_pkey PRIMARY KEY (id);
 H   ALTER TABLE ONLY public.bounding_box DROP CONSTRAINT bounding_box_pkey;
       public            postgres    false    228            m           1259    544830    bounding_box_geom_idx    INDEX     M   CREATE INDEX bounding_box_geom_idx ON public.bounding_box USING gist (geom);
 )   DROP INDEX public.bounding_box_geom_idx;
       public            postgres    false    228            n           1259    544829    bounding_box_id_idx    INDEX     J   CREATE INDEX bounding_box_id_idx ON public.bounding_box USING btree (id);
 '   DROP INDEX public.bounding_box_id_idx;
       public            postgres    false    228            
   �   x���1�0���WtlA�%�\rc�4.b\7�$X�����������$ d)�H�S�f^�}j�n��DR��ȝ��)�o�>)1:������4�8���_������ú�V�Dn���Mc����9tL�+$@�3|�?�9\��~<���4\n�U!��F�     