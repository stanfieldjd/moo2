/*
 * Master of Orion II v1.31: isolated C reconstruction of the ENTIRE
 * Load_H_And_Pro_File_Strings_ original Watcom function (0xBE0E5, 2996 bytes).
 * Not original MicroProse source, not original copyrighted text.
 *
 * The original is exactly 199 repetitions of:
 *    MOV EAX, string_id; CALL E_Strings_; MOV [DATA+dst], EAX
 * followed by a final one-DWORD global copy and RET.
 * E_Strings_ reads from _strings (DATA object 2 offset 0x2E578).
 * The string table MUST have been initialized by Load_E_Strings_ first.
 *
 * This file expects the emulated original v1.31 DATA object 2 buffer
 * (at least 384208 bytes) and preserves the original little-endian
 * 32-bit virtual addresses. This is NOT a host char* implementation.
 * Caller must supply valid original-format initialized storage.
 */
#include <stddef.h>
#include <stdint.h>

typedef struct {
    uint16_t original_string_id;
    uint32_t data_destination_offset;
} Moo2V131StringBinding;

static const Moo2V131StringBinding kMoo2HProBindings[] = {
    { 616u, 0x1ffa0u }, /* _personality_labels */
    { 617u, 0x1ffa4u },
    { 618u, 0x1ffa8u },
    { 619u, 0x1ffacu },
    { 620u, 0x1ffb0u },
    { 621u, 0x1ffb4u },
    { 622u, 0x1ffb8u },
    { 623u, 0x1a210u }, /* _objective_labels */
    { 624u, 0x1a214u },
    { 625u, 0x1a218u },
    { 626u, 0x1a21cu },
    { 627u, 0x1a220u },
    { 628u, 0x1a224u },
    { 629u, 0x21150u }, /* _treaty_labels */
    { 630u, 0x21154u },
    { 631u, 0x21158u },
    { 632u, 0x2115cu },
    { 633u, 0x21160u },
    { 634u, 0x21164u },
    { 635u, 0x21168u },
    { 636u, 0x1a228u }, /* _government_labels */
    { 637u, 0x1a22cu },
    { 638u, 0x1a230u },
    { 639u, 0x1a234u },
    { 640u, 0x1a238u },
    { 641u, 0x1a23cu },
    { 642u, 0x1a240u },
    { 643u, 0x1a244u },
    { 645u, 0x1a630u }, /* _race_names */
    { 646u, 0x1a634u },
    { 647u, 0x1a638u },
    { 648u, 0x1a63cu },
    { 649u, 0x1a640u },
    { 650u, 0x1a644u },
    { 651u, 0x1a648u },
    { 652u, 0x1a64cu },
    { 653u, 0x1a650u },
    { 654u, 0x1a654u },
    { 655u, 0x1a658u },
    { 656u, 0x1a65cu },
    { 657u, 0x1a660u },
    { 658u, 0x1a664u },
    { 659u, 0x1a668u },
    { 173u, 0x1a66cu },
    { 246u, 0x1a670u },
    { 272u, 0x1a674u },
    { 281u, 0x1a678u },
    { 324u, 0x1a67cu },
    { 142u, 0x1ac08u }, /* _help_category_labels */
    { 660u, 0x1ac0cu },
    { 661u, 0x1ac10u },
    { 662u, 0x1ac14u },
    { 663u, 0x1ac18u },
    { 664u, 0x1ac1cu },
    { 665u, 0x1ac20u },
    { 666u, 0x1ac24u },
    { 667u, 0x1ac28u },
    { 668u, 0x1ac2cu },
    { 669u, 0x1ac30u },
    { 670u, 0x1ac34u },
    { 671u, 0x1ac38u },
    { 672u, 0x1ac3cu },
    { 673u, 0x1ac40u },
    { 674u, 0x1ac44u },
    { 675u, 0x1ac48u },
    { 676u, 0x1ac58u }, /* _spectral_class_string */
    { 677u, 0x1ac5cu },
    { 678u, 0x1ac60u },
    { 679u, 0x1ac64u },
    { 680u, 0x1ac68u },
    { 681u, 0x1ac6cu },
    { 682u, 0x1ac70u },
    { 683u, 0x1abe0u }, /* _planet_size_string */
    { 480u, 0x1abe4u },
    { 371u, 0x1abe8u },
    { 360u, 0x1abecu },
    { 323u, 0x1abf0u },
    { 684u, 0x1abf4u }, /* _mineral_class_string */
    { 423u, 0x1abf8u },
    { 685u, 0x1abfcu },
    { 450u, 0x1ac00u },
    { 686u, 0x1ac04u },
    { 687u, 0x1ac74u }, /* _planet_gravity_string */
    { 688u, 0x1ac78u },
    { 689u, 0x1ac7cu },
    { 690u, 0x1ac4cu }, /* _planet_atmosphere_string */
    { 691u, 0x1ac50u },
    { 692u, 0x1ac54u },
    { 693u, 0x179e8u }, /* _planet_group_string */
    { 694u, 0x179ecu },
    { 695u, 0x179f0u },
    { 696u, 0x179f4u },
    { 697u, 0x179b8u }, /* _planet_special_string */
    { 698u, 0x179bcu },
    { 699u, 0x179c0u },
    { 700u, 0x179c4u },
    { 701u, 0x179c8u },
    { 702u, 0x179ccu },
    { 703u, 0x179d0u },
    { 704u, 0x179d4u },
    { 705u, 0x179d8u },
    { 706u, 0x179dcu },
    { 707u, 0x179e0u },
    { 708u, 0x179e4u },
    { 709u, 0x17968u }, /* _planet_type_string */
    { 710u, 0x1796cu },
    { 711u, 0x17970u },
    { 712u, 0x17974u },
    { 713u, 0x17978u },
    { 714u, 0x1797cu },
    { 715u, 0x17980u },
    { 716u, 0x17984u },
    { 717u, 0x17988u },
    { 718u, 0x1798cu },
    { 539u, 0x17990u }, /* _planet_climate_string */
    { 719u, 0x17994u },
    { 720u, 0x17998u },
    { 721u, 0x1799cu },
    { 722u, 0x179a0u },
    { 399u, 0x179a4u },
    { 501u, 0x179a8u },
    { 184u, 0x179acu },
    { 723u, 0x179b0u },
    { 303u, 0x179b4u },
    { 724u, 0x5222u },
    { 725u, 0x5234u },
    { 726u, 0x5246u },
    { 727u, 0x5258u },
    { 623u, 0x526au },
    { 728u, 0x527cu },
    { 729u, 0x528eu },
    { 730u, 0x52a0u },
    { 731u, 0x52b2u },
    { 732u, 0x52c4u },
    { 733u, 0x52d6u },
    { 734u, 0x52e8u },
    { 735u, 0x52fau },
    { 736u, 0x530cu },
    { 737u, 0x531eu },
    { 738u, 0x5330u },
    { 739u, 0x5342u },
    { 740u, 0x5354u },
    { 741u, 0x5366u },
    { 742u, 0x5378u },
    { 743u, 0x538au },
    { 744u, 0x539cu },
    { 745u, 0x53aeu },
    { 746u, 0x53c0u },
    { 747u, 0x53d2u },
    { 748u, 0x53e4u },
    { 749u, 0x53f6u },
    { 750u, 0x5408u },
    { 751u, 0x541au },
    { 752u, 0x542cu },
    { 753u, 0x543eu },
    { 754u, 0x5450u },
    { 755u, 0x5462u },
    { 756u, 0x5474u },
    { 757u, 0x5486u },
    { 758u, 0x5498u },
    { 759u, 0x54aau },
    { 760u, 0x54bcu },
    { 761u, 0x54ceu },
    { 762u, 0x54e0u },
    { 672u, 0x54f2u },
    { 763u, 0x5504u },
    { 764u, 0x5516u },
    { 765u, 0x5528u },
    { 766u, 0x553au },
    { 767u, 0x554cu },
    { 768u, 0x555eu },
    { 769u, 0x5570u },
    { 770u, 0x5582u },
    { 771u, 0x5594u },
    { 772u, 0x55a6u },
    { 773u, 0x55b8u },
    { 774u, 0x55cau },
    { 775u, 0x55dcu },
    { 731u, 0x1b130u }, /* _admin_skill_names */
    { 735u, 0x1b134u },
    { 739u, 0x1b138u },
    { 745u, 0x1b13cu },
    { 747u, 0x1b140u },
    { 749u, 0x1b144u },
    { 761u, 0x1b148u },
    { 764u, 0x1b14cu },
    { 768u, 0x1b150u },
    { 776u, 0x18430u }, /* _officer_level_names */
    { 777u, 0x18434u },
    { 778u, 0x18438u },
    { 779u, 0x1843cu },
    { 780u, 0x18440u },
    { 781u, 0x18444u },
    { 782u, 0x18448u }, /* _star_officer_level_names */
    { 783u, 0x1844cu },
    { 784u, 0x18450u },
    { 785u, 0x18454u },
    { 786u, 0x18458u },
    { 787u, 0x1845cu },
};

static uint32_t moo2_v131_get_le32(const uint8_t *source)
{
    return (uint32_t)source[0] | ((uint32_t)source[1] << 8)
         | ((uint32_t)source[2] << 16) | ((uint32_t)source[3] << 24);
}

static void moo2_v131_set_le32(uint8_t *destination, uint32_t word)
{
    destination[0] = (uint8_t)word;
    destination[1] = (uint8_t)(word >> 8);
    destination[2] = (uint8_t)(word >> 16);
    destination[3] = (uint8_t)(word >> 24);
}

void moo2_v131_derived_load_h_and_pro_file_strings(uint8_t *data_object2)
{
    for (size_t i = 0; i < sizeof(kMoo2HProBindings)/sizeof(kMoo2HProBindings[0]); ++i) {
        const uint32_t id = kMoo2HProBindings[i].original_string_id;
        const uint32_t dest = kMoo2HProBindings[i].data_destination_offset;
        uint32_t ptr = moo2_v131_get_le32(data_object2 + 0x2E578u + 4u*id);
        moo2_v131_set_le32(data_object2 + dest, ptr);
    }
    /* Original final MOV [DATA+0x21170], [DATA+0x2EF88]. */
    moo2_v131_set_le32(data_object2 + 0x21170u,
                        moo2_v131_get_le32(data_object2 + 0x2EF88u));
}
