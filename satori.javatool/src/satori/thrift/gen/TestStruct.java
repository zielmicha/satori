/**
 * Autogenerated by Thrift
 *
 * DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
 */
package satori.thrift.gen;

import java.util.List;
import java.util.ArrayList;
import java.util.Map;
import java.util.HashMap;
import java.util.EnumMap;
import java.util.Set;
import java.util.HashSet;
import java.util.EnumSet;
import java.util.Collections;
import java.util.BitSet;
import java.nio.ByteBuffer;
import java.util.Arrays;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import org.apache.thrift.*;
import org.apache.thrift.async.*;
import org.apache.thrift.meta_data.*;
import org.apache.thrift.transport.*;
import org.apache.thrift.protocol.*;

public class TestStruct implements TBase<TestStruct, TestStruct._Fields>, java.io.Serializable, Cloneable {
  private static final TStruct STRUCT_DESC = new TStruct("TestStruct");

  private static final TField ID_FIELD_DESC = new TField("id", TType.I64, (short)1);
  private static final TField PROBLEM_FIELD_DESC = new TField("problem", TType.I64, (short)2);
  private static final TField NAME_FIELD_DESC = new TField("name", TType.STRING, (short)3);
  private static final TField DESCRIPTION_FIELD_DESC = new TField("description", TType.STRING, (short)4);
  private static final TField ENVIRONMENT_FIELD_DESC = new TField("environment", TType.STRING, (short)5);
  private static final TField OBSOLETE_FIELD_DESC = new TField("obsolete", TType.BOOL, (short)6);

  public long id;
  public long problem;
  public String name;
  public String description;
  public String environment;
  public boolean obsolete;

  /** The set of fields this struct contains, along with convenience methods for finding and manipulating them. */
  public enum _Fields implements TFieldIdEnum {
    ID((short)1, "id"),
    PROBLEM((short)2, "problem"),
    NAME((short)3, "name"),
    DESCRIPTION((short)4, "description"),
    ENVIRONMENT((short)5, "environment"),
    OBSOLETE((short)6, "obsolete");

    private static final Map<String, _Fields> byName = new HashMap<String, _Fields>();

    static {
      for (_Fields field : EnumSet.allOf(_Fields.class)) {
        byName.put(field.getFieldName(), field);
      }
    }

    /**
     * Find the _Fields constant that matches fieldId, or null if its not found.
     */
    public static _Fields findByThriftId(int fieldId) {
      switch(fieldId) {
        case 1: // ID
          return ID;
        case 2: // PROBLEM
          return PROBLEM;
        case 3: // NAME
          return NAME;
        case 4: // DESCRIPTION
          return DESCRIPTION;
        case 5: // ENVIRONMENT
          return ENVIRONMENT;
        case 6: // OBSOLETE
          return OBSOLETE;
        default:
          return null;
      }
    }

    /**
     * Find the _Fields constant that matches fieldId, throwing an exception
     * if it is not found.
     */
    public static _Fields findByThriftIdOrThrow(int fieldId) {
      _Fields fields = findByThriftId(fieldId);
      if (fields == null) throw new IllegalArgumentException("Field " + fieldId + " doesn't exist!");
      return fields;
    }

    /**
     * Find the _Fields constant that matches name, or null if its not found.
     */
    public static _Fields findByName(String name) {
      return byName.get(name);
    }

    private final short _thriftId;
    private final String _fieldName;

    _Fields(short thriftId, String fieldName) {
      _thriftId = thriftId;
      _fieldName = fieldName;
    }

    public short getThriftFieldId() {
      return _thriftId;
    }

    public String getFieldName() {
      return _fieldName;
    }
  }

  // isset id assignments
  private static final int __ID_ISSET_ID = 0;
  private static final int __PROBLEM_ISSET_ID = 1;
  private static final int __OBSOLETE_ISSET_ID = 2;
  private BitSet __isset_bit_vector = new BitSet(3);

  public static final Map<_Fields, FieldMetaData> metaDataMap;
  static {
    Map<_Fields, FieldMetaData> tmpMap = new EnumMap<_Fields, FieldMetaData>(_Fields.class);
    tmpMap.put(_Fields.ID, new FieldMetaData("id", TFieldRequirementType.OPTIONAL, 
        new FieldValueMetaData(TType.I64)));
    tmpMap.put(_Fields.PROBLEM, new FieldMetaData("problem", TFieldRequirementType.OPTIONAL, 
        new FieldValueMetaData(TType.I64        , "ProblemId")));
    tmpMap.put(_Fields.NAME, new FieldMetaData("name", TFieldRequirementType.OPTIONAL, 
        new FieldValueMetaData(TType.STRING)));
    tmpMap.put(_Fields.DESCRIPTION, new FieldMetaData("description", TFieldRequirementType.OPTIONAL, 
        new FieldValueMetaData(TType.STRING)));
    tmpMap.put(_Fields.ENVIRONMENT, new FieldMetaData("environment", TFieldRequirementType.OPTIONAL, 
        new FieldValueMetaData(TType.STRING)));
    tmpMap.put(_Fields.OBSOLETE, new FieldMetaData("obsolete", TFieldRequirementType.OPTIONAL, 
        new FieldValueMetaData(TType.BOOL)));
    metaDataMap = Collections.unmodifiableMap(tmpMap);
    FieldMetaData.addStructMetaDataMap(TestStruct.class, metaDataMap);
  }

  public TestStruct() {
  }

  /**
   * Performs a deep copy on <i>other</i>.
   */
  public TestStruct(TestStruct other) {
    __isset_bit_vector.clear();
    __isset_bit_vector.or(other.__isset_bit_vector);
    this.id = other.id;
    this.problem = other.problem;
    if (other.isSetName()) {
      this.name = other.name;
    }
    if (other.isSetDescription()) {
      this.description = other.description;
    }
    if (other.isSetEnvironment()) {
      this.environment = other.environment;
    }
    this.obsolete = other.obsolete;
  }

  public TestStruct deepCopy() {
    return new TestStruct(this);
  }

  @Override
  public void clear() {
    setIdIsSet(false);
    this.id = 0;
    setProblemIsSet(false);
    this.problem = 0;
    this.name = null;
    this.description = null;
    this.environment = null;
    setObsoleteIsSet(false);
    this.obsolete = false;
  }

  public long getId() {
    return this.id;
  }

  public TestStruct setId(long id) {
    this.id = id;
    setIdIsSet(true);
    return this;
  }

  public void unsetId() {
    __isset_bit_vector.clear(__ID_ISSET_ID);
  }

  /** Returns true if field id is set (has been asigned a value) and false otherwise */
  public boolean isSetId() {
    return __isset_bit_vector.get(__ID_ISSET_ID);
  }

  public void setIdIsSet(boolean value) {
    __isset_bit_vector.set(__ID_ISSET_ID, value);
  }

  public long getProblem() {
    return this.problem;
  }

  public TestStruct setProblem(long problem) {
    this.problem = problem;
    setProblemIsSet(true);
    return this;
  }

  public void unsetProblem() {
    __isset_bit_vector.clear(__PROBLEM_ISSET_ID);
  }

  /** Returns true if field problem is set (has been asigned a value) and false otherwise */
  public boolean isSetProblem() {
    return __isset_bit_vector.get(__PROBLEM_ISSET_ID);
  }

  public void setProblemIsSet(boolean value) {
    __isset_bit_vector.set(__PROBLEM_ISSET_ID, value);
  }

  public String getName() {
    return this.name;
  }

  public TestStruct setName(String name) {
    this.name = name;
    return this;
  }

  public void unsetName() {
    this.name = null;
  }

  /** Returns true if field name is set (has been asigned a value) and false otherwise */
  public boolean isSetName() {
    return this.name != null;
  }

  public void setNameIsSet(boolean value) {
    if (!value) {
      this.name = null;
    }
  }

  public String getDescription() {
    return this.description;
  }

  public TestStruct setDescription(String description) {
    this.description = description;
    return this;
  }

  public void unsetDescription() {
    this.description = null;
  }

  /** Returns true if field description is set (has been asigned a value) and false otherwise */
  public boolean isSetDescription() {
    return this.description != null;
  }

  public void setDescriptionIsSet(boolean value) {
    if (!value) {
      this.description = null;
    }
  }

  public String getEnvironment() {
    return this.environment;
  }

  public TestStruct setEnvironment(String environment) {
    this.environment = environment;
    return this;
  }

  public void unsetEnvironment() {
    this.environment = null;
  }

  /** Returns true if field environment is set (has been asigned a value) and false otherwise */
  public boolean isSetEnvironment() {
    return this.environment != null;
  }

  public void setEnvironmentIsSet(boolean value) {
    if (!value) {
      this.environment = null;
    }
  }

  public boolean isObsolete() {
    return this.obsolete;
  }

  public TestStruct setObsolete(boolean obsolete) {
    this.obsolete = obsolete;
    setObsoleteIsSet(true);
    return this;
  }

  public void unsetObsolete() {
    __isset_bit_vector.clear(__OBSOLETE_ISSET_ID);
  }

  /** Returns true if field obsolete is set (has been asigned a value) and false otherwise */
  public boolean isSetObsolete() {
    return __isset_bit_vector.get(__OBSOLETE_ISSET_ID);
  }

  public void setObsoleteIsSet(boolean value) {
    __isset_bit_vector.set(__OBSOLETE_ISSET_ID, value);
  }

  public void setFieldValue(_Fields field, Object value) {
    switch (field) {
    case ID:
      if (value == null) {
        unsetId();
      } else {
        setId((Long)value);
      }
      break;

    case PROBLEM:
      if (value == null) {
        unsetProblem();
      } else {
        setProblem((Long)value);
      }
      break;

    case NAME:
      if (value == null) {
        unsetName();
      } else {
        setName((String)value);
      }
      break;

    case DESCRIPTION:
      if (value == null) {
        unsetDescription();
      } else {
        setDescription((String)value);
      }
      break;

    case ENVIRONMENT:
      if (value == null) {
        unsetEnvironment();
      } else {
        setEnvironment((String)value);
      }
      break;

    case OBSOLETE:
      if (value == null) {
        unsetObsolete();
      } else {
        setObsolete((Boolean)value);
      }
      break;

    }
  }

  public Object getFieldValue(_Fields field) {
    switch (field) {
    case ID:
      return new Long(getId());

    case PROBLEM:
      return new Long(getProblem());

    case NAME:
      return getName();

    case DESCRIPTION:
      return getDescription();

    case ENVIRONMENT:
      return getEnvironment();

    case OBSOLETE:
      return new Boolean(isObsolete());

    }
    throw new IllegalStateException();
  }

  /** Returns true if field corresponding to fieldID is set (has been asigned a value) and false otherwise */
  public boolean isSet(_Fields field) {
    if (field == null) {
      throw new IllegalArgumentException();
    }

    switch (field) {
    case ID:
      return isSetId();
    case PROBLEM:
      return isSetProblem();
    case NAME:
      return isSetName();
    case DESCRIPTION:
      return isSetDescription();
    case ENVIRONMENT:
      return isSetEnvironment();
    case OBSOLETE:
      return isSetObsolete();
    }
    throw new IllegalStateException();
  }

  @Override
  public boolean equals(Object that) {
    if (that == null)
      return false;
    if (that instanceof TestStruct)
      return this.equals((TestStruct)that);
    return false;
  }

  public boolean equals(TestStruct that) {
    if (that == null)
      return false;

    boolean this_present_id = true && this.isSetId();
    boolean that_present_id = true && that.isSetId();
    if (this_present_id || that_present_id) {
      if (!(this_present_id && that_present_id))
        return false;
      if (this.id != that.id)
        return false;
    }

    boolean this_present_problem = true && this.isSetProblem();
    boolean that_present_problem = true && that.isSetProblem();
    if (this_present_problem || that_present_problem) {
      if (!(this_present_problem && that_present_problem))
        return false;
      if (this.problem != that.problem)
        return false;
    }

    boolean this_present_name = true && this.isSetName();
    boolean that_present_name = true && that.isSetName();
    if (this_present_name || that_present_name) {
      if (!(this_present_name && that_present_name))
        return false;
      if (!this.name.equals(that.name))
        return false;
    }

    boolean this_present_description = true && this.isSetDescription();
    boolean that_present_description = true && that.isSetDescription();
    if (this_present_description || that_present_description) {
      if (!(this_present_description && that_present_description))
        return false;
      if (!this.description.equals(that.description))
        return false;
    }

    boolean this_present_environment = true && this.isSetEnvironment();
    boolean that_present_environment = true && that.isSetEnvironment();
    if (this_present_environment || that_present_environment) {
      if (!(this_present_environment && that_present_environment))
        return false;
      if (!this.environment.equals(that.environment))
        return false;
    }

    boolean this_present_obsolete = true && this.isSetObsolete();
    boolean that_present_obsolete = true && that.isSetObsolete();
    if (this_present_obsolete || that_present_obsolete) {
      if (!(this_present_obsolete && that_present_obsolete))
        return false;
      if (this.obsolete != that.obsolete)
        return false;
    }

    return true;
  }

  @Override
  public int hashCode() {
    return 0;
  }

  public int compareTo(TestStruct other) {
    if (!getClass().equals(other.getClass())) {
      return getClass().getName().compareTo(other.getClass().getName());
    }

    int lastComparison = 0;
    TestStruct typedOther = (TestStruct)other;

    lastComparison = Boolean.valueOf(isSetId()).compareTo(typedOther.isSetId());
    if (lastComparison != 0) {
      return lastComparison;
    }
    if (isSetId()) {
      lastComparison = TBaseHelper.compareTo(this.id, typedOther.id);
      if (lastComparison != 0) {
        return lastComparison;
      }
    }
    lastComparison = Boolean.valueOf(isSetProblem()).compareTo(typedOther.isSetProblem());
    if (lastComparison != 0) {
      return lastComparison;
    }
    if (isSetProblem()) {
      lastComparison = TBaseHelper.compareTo(this.problem, typedOther.problem);
      if (lastComparison != 0) {
        return lastComparison;
      }
    }
    lastComparison = Boolean.valueOf(isSetName()).compareTo(typedOther.isSetName());
    if (lastComparison != 0) {
      return lastComparison;
    }
    if (isSetName()) {
      lastComparison = TBaseHelper.compareTo(this.name, typedOther.name);
      if (lastComparison != 0) {
        return lastComparison;
      }
    }
    lastComparison = Boolean.valueOf(isSetDescription()).compareTo(typedOther.isSetDescription());
    if (lastComparison != 0) {
      return lastComparison;
    }
    if (isSetDescription()) {
      lastComparison = TBaseHelper.compareTo(this.description, typedOther.description);
      if (lastComparison != 0) {
        return lastComparison;
      }
    }
    lastComparison = Boolean.valueOf(isSetEnvironment()).compareTo(typedOther.isSetEnvironment());
    if (lastComparison != 0) {
      return lastComparison;
    }
    if (isSetEnvironment()) {
      lastComparison = TBaseHelper.compareTo(this.environment, typedOther.environment);
      if (lastComparison != 0) {
        return lastComparison;
      }
    }
    lastComparison = Boolean.valueOf(isSetObsolete()).compareTo(typedOther.isSetObsolete());
    if (lastComparison != 0) {
      return lastComparison;
    }
    if (isSetObsolete()) {
      lastComparison = TBaseHelper.compareTo(this.obsolete, typedOther.obsolete);
      if (lastComparison != 0) {
        return lastComparison;
      }
    }
    return 0;
  }

  public _Fields fieldForId(int fieldId) {
    return _Fields.findByThriftId(fieldId);
  }

  public void read(TProtocol iprot) throws TException {
    TField field;
    iprot.readStructBegin();
    while (true)
    {
      field = iprot.readFieldBegin();
      if (field.type == TType.STOP) { 
        break;
      }
      switch (field.id) {
        case 1: // ID
          if (field.type == TType.I64) {
            this.id = iprot.readI64();
            setIdIsSet(true);
          } else { 
            TProtocolUtil.skip(iprot, field.type);
          }
          break;
        case 2: // PROBLEM
          if (field.type == TType.I64) {
            this.problem = iprot.readI64();
            setProblemIsSet(true);
          } else { 
            TProtocolUtil.skip(iprot, field.type);
          }
          break;
        case 3: // NAME
          if (field.type == TType.STRING) {
            this.name = iprot.readString();
          } else { 
            TProtocolUtil.skip(iprot, field.type);
          }
          break;
        case 4: // DESCRIPTION
          if (field.type == TType.STRING) {
            this.description = iprot.readString();
          } else { 
            TProtocolUtil.skip(iprot, field.type);
          }
          break;
        case 5: // ENVIRONMENT
          if (field.type == TType.STRING) {
            this.environment = iprot.readString();
          } else { 
            TProtocolUtil.skip(iprot, field.type);
          }
          break;
        case 6: // OBSOLETE
          if (field.type == TType.BOOL) {
            this.obsolete = iprot.readBool();
            setObsoleteIsSet(true);
          } else { 
            TProtocolUtil.skip(iprot, field.type);
          }
          break;
        default:
          TProtocolUtil.skip(iprot, field.type);
      }
      iprot.readFieldEnd();
    }
    iprot.readStructEnd();

    // check for required fields of primitive type, which can't be checked in the validate method
    validate();
  }

  public void write(TProtocol oprot) throws TException {
    validate();

    oprot.writeStructBegin(STRUCT_DESC);
    if (isSetId()) {
      oprot.writeFieldBegin(ID_FIELD_DESC);
      oprot.writeI64(this.id);
      oprot.writeFieldEnd();
    }
    if (isSetProblem()) {
      oprot.writeFieldBegin(PROBLEM_FIELD_DESC);
      oprot.writeI64(this.problem);
      oprot.writeFieldEnd();
    }
    if (this.name != null) {
      if (isSetName()) {
        oprot.writeFieldBegin(NAME_FIELD_DESC);
        oprot.writeString(this.name);
        oprot.writeFieldEnd();
      }
    }
    if (this.description != null) {
      if (isSetDescription()) {
        oprot.writeFieldBegin(DESCRIPTION_FIELD_DESC);
        oprot.writeString(this.description);
        oprot.writeFieldEnd();
      }
    }
    if (this.environment != null) {
      if (isSetEnvironment()) {
        oprot.writeFieldBegin(ENVIRONMENT_FIELD_DESC);
        oprot.writeString(this.environment);
        oprot.writeFieldEnd();
      }
    }
    if (isSetObsolete()) {
      oprot.writeFieldBegin(OBSOLETE_FIELD_DESC);
      oprot.writeBool(this.obsolete);
      oprot.writeFieldEnd();
    }
    oprot.writeFieldStop();
    oprot.writeStructEnd();
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder("TestStruct(");
    boolean first = true;

    if (isSetId()) {
      sb.append("id:");
      sb.append(this.id);
      first = false;
    }
    if (isSetProblem()) {
      if (!first) sb.append(", ");
      sb.append("problem:");
      sb.append(this.problem);
      first = false;
    }
    if (isSetName()) {
      if (!first) sb.append(", ");
      sb.append("name:");
      if (this.name == null) {
        sb.append("null");
      } else {
        sb.append(this.name);
      }
      first = false;
    }
    if (isSetDescription()) {
      if (!first) sb.append(", ");
      sb.append("description:");
      if (this.description == null) {
        sb.append("null");
      } else {
        sb.append(this.description);
      }
      first = false;
    }
    if (isSetEnvironment()) {
      if (!first) sb.append(", ");
      sb.append("environment:");
      if (this.environment == null) {
        sb.append("null");
      } else {
        sb.append(this.environment);
      }
      first = false;
    }
    if (isSetObsolete()) {
      if (!first) sb.append(", ");
      sb.append("obsolete:");
      sb.append(this.obsolete);
      first = false;
    }
    sb.append(")");
    return sb.toString();
  }

  public void validate() throws TException {
    // check for required fields
  }

}

