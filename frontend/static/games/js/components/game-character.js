/**
 * GameCharacter — 3D Playable Character Controller using Three.js.
 * Supports WASD keyboard movement, Click-to-Move, and smooth camera tracking.
 */
class GameCharacter {
  constructor(scene, camera) {
    this.scene = scene;
    this.camera = camera;
    this.position = new THREE.Vector3(-2, 0, 3);
    this.targetPosition = null;
    this.speed = 0.12;
    this.rotation = 0;
    this.isMoving = false;
    this.walkCycle = 0;

    // Movement key states
    this.keys = { forward: false, backward: false, left: false, right: false };

    this.init3DModel();
    this.initEventListeners();
  }

  init3DModel() {
    this.mesh = new THREE.Group();

    // Materials
    const skinMat = new THREE.MeshStandardMaterial({ color: 0xFFDBAC, roughness: 0.6 });
    const shirtMat = new THREE.MeshStandardMaterial({ color: 0x3B82F6, roughness: 0.5 }); // Blue builder shirt
    const pantsMat = new THREE.MeshStandardMaterial({ color: 0x1E293B, roughness: 0.7 }); // Dark jeans
    const vestMat = new THREE.MeshStandardMaterial({ color: 0xF59E0B, roughness: 0.4 });  // Safety vest
    const hatMat = new THREE.MeshStandardMaterial({ color: 0xFBBF24, roughness: 0.3, metalness: 0.1 }); // Yellow hardhat
    const shoeMat = new THREE.MeshStandardMaterial({ color: 0x451A03, roughness: 0.8 });

    // Torso / Body
    const torso = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.9, 0.4), shirtMat);
    torso.position.y = 1.1;
    torso.castShadow = true;
    this.mesh.add(torso);

    // Safety Vest Over Torso
    const vest = new THREE.Mesh(new THREE.BoxGeometry(0.74, 0.7, 0.44), vestMat);
    vest.position.y = 1.15;
    vest.castShadow = true;
    this.mesh.add(vest);

    // Head
    const head = new THREE.Mesh(new THREE.BoxGeometry(0.48, 0.48, 0.44), skinMat);
    head.position.y = 1.8;
    head.castShadow = true;
    this.mesh.add(head);

    // Builder Hardhat
    const hatDome = new THREE.Mesh(new THREE.SphereGeometry(0.32, 12, 8, 0, Math.PI * 2, 0, Math.PI / 2), hatMat);
    hatDome.position.y = 2.02;
    this.mesh.add(hatDome);
    const hatBrim = new THREE.Mesh(new THREE.CylinderGeometry(0.38, 0.38, 0.06, 12), hatMat);
    hatBrim.position.y = 2.02;
    this.mesh.add(hatBrim);

    // Left Arm & Right Arm
    this.leftArm = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.7, 0.2), shirtMat);
    this.leftArm.position.set(-0.48, 1.1, 0);
    this.leftArm.castShadow = true;
    this.mesh.add(this.leftArm);

    this.rightArm = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.7, 0.2), shirtMat);
    this.rightArm.position.set(0.48, 1.1, 0);
    this.rightArm.castShadow = true;
    this.mesh.add(this.rightArm);

    // Left Leg & Right Leg
    this.leftLeg = new THREE.Mesh(new THREE.BoxGeometry(0.26, 0.7, 0.26), pantsMat);
    this.leftLeg.position.set(-0.2, 0.45, 0);
    this.leftLeg.castShadow = true;
    this.mesh.add(this.leftLeg);

    this.rightLeg = new THREE.Mesh(new THREE.BoxGeometry(0.26, 0.7, 0.26), pantsMat);
    this.rightLeg.position.set(0.2, 0.45, 0);
    this.rightLeg.castShadow = true;
    this.mesh.add(this.rightLeg);

    // Character Shadow / Target Circle
    const shadowGeo = new THREE.RingGeometry(0.2, 0.6, 16);
    const shadowMat = new THREE.MeshBasicMaterial({ color: 0x000000, opacity: 0.3, transparent: true, side: THREE.DoubleSide });
    this.groundRing = new THREE.Mesh(shadowGeo, shadowMat);
    this.groundRing.rotation.x = -Math.PI / 2;
    this.groundRing.position.y = 0.02;
    this.mesh.add(this.groundRing);

    // Position in Scene
    this.mesh.position.copy(this.position);
    this.scene.add(this.mesh);

    // Destination target ring (for click-to-move)
    const targetRingGeo = new THREE.RingGeometry(0.4, 0.6, 24);
    const targetRingMat = new THREE.MeshBasicMaterial({ color: 0x38BDF8, side: THREE.DoubleSide });
    this.clickTargetMesh = new THREE.Mesh(targetRingGeo, targetRingMat);
    this.clickTargetMesh.rotation.x = -Math.PI / 2;
    this.clickTargetMesh.position.y = 0.03;
    this.clickTargetMesh.visible = false;
    this.scene.add(this.clickTargetMesh);
  }

  initEventListeners() {
    window.addEventListener('keydown', (e) => this.onKeyDown(e));
    window.addEventListener('keyup', (e) => this.onKeyUp(e));
  }

  onKeyDown(e) {
    const k = e.key.toLowerCase();
    if (k === 'w' || k === 'arrowup') this.keys.forward = true;
    if (k === 's' || k === 'arrowdown') this.keys.backward = true;
    if (k === 'a' || k === 'arrowleft') this.keys.left = true;
    if (k === 'd' || k === 'arrowright') this.keys.right = true;
    this.targetPosition = null; // Keyboard cancels click-to-move
  }

  onKeyUp(e) {
    const k = e.key.toLowerCase();
    if (k === 'w' || k === 'arrowup') this.keys.forward = false;
    if (k === 's' || k === 'arrowdown') this.keys.backward = false;
    if (k === 'a' || k === 'arrowleft') this.keys.left = false;
    if (k === 'd' || k === 'arrowright') this.keys.right = false;
  }

  moveTo(worldPoint) {
    this.targetPosition = new THREE.Vector3(worldPoint.x, 0, worldPoint.z);
    this.clickTargetMesh.position.set(worldPoint.x, 0.03, worldPoint.z);
    this.clickTargetMesh.visible = true;
  }

  update() {
    let moveX = 0;
    let moveZ = 0;

    // 1. Check Keyboard WASD
    if (this.keys.forward) moveZ -= 1;
    if (this.keys.backward) moveZ += 1;
    if (this.keys.left) moveX -= 1;
    if (this.keys.right) moveX += 1;

    if (moveX !== 0 || moveZ !== 0) {
      const len = Math.sqrt(moveX * moveX + moveZ * moveZ);
      this.position.x += (moveX / len) * this.speed;
      this.position.z += (moveZ / len) * this.speed;
      this.rotation = Math.atan2(moveX, moveZ);
      this.isMoving = true;
    } else if (this.targetPosition) {
      // 2. Click-to-move pathing
      const diff = new THREE.Vector3().subVectors(this.targetPosition, this.position);
      diff.y = 0;
      const dist = diff.length();

      if (dist > 0.2) {
        diff.normalize();
        this.position.x += diff.x * this.speed;
        this.position.z += diff.z * this.speed;
        this.rotation = Math.atan2(diff.x, diff.z);
        this.isMoving = true;
      } else {
        this.targetPosition = null;
        this.clickTargetMesh.visible = false;
        this.isMoving = false;
      }
    } else {
      this.isMoving = false;
    }

    // Boundary constraints (stay within island radius)
    const islandRadius = 14;
    const distFromCenter = Math.sqrt(this.position.x * this.position.x + this.position.z * this.position.z);
    if (distFromCenter > islandRadius) {
      const angle = Math.atan2(this.position.z, this.position.x);
      this.position.x = Math.cos(angle) * islandRadius;
      this.position.z = Math.sin(angle) * islandRadius;
    }

    // Apply Position & Rotation to Mesh
    this.mesh.position.set(this.position.x, 0, this.position.z);
    this.mesh.rotation.y = this.rotation;

    // Walking Animation (Legs and arms swing)
    if (this.isMoving) {
      this.walkCycle += 0.25;
      this.leftLeg.rotation.x = Math.sin(this.walkCycle) * 0.6;
      this.rightLeg.rotation.x = -Math.sin(this.walkCycle) * 0.6;
      this.leftArm.rotation.x = -Math.sin(this.walkCycle) * 0.6;
      this.rightArm.rotation.x = Math.sin(this.walkCycle) * 0.6;
    } else {
      this.leftLeg.rotation.x = 0;
      this.rightLeg.rotation.x = 0;
      this.leftArm.rotation.x = 0;
      this.rightArm.rotation.x = 0;
    }
  }
}

window.GameCharacter = GameCharacter;
